from django.shortcuts import redirect, render , get_object_or_404
from django.http import JsonResponse
from .models import Invoice, Payment, UnpaidReasonLog
from orders.models import Order, OrderItem, OrderStatus, DailyOrderCounter
from reservations.models import Table
from django.db import transaction
from core.decorators import staff_member_required, admin_required
from django.db.models import Sum, Avg, Q, F, Count
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date, time
from decimal import Decimal
import json
from django.views.decorators.http import require_http_methods


@staff_member_required
@transaction.atomic
def generate_invoice_by_table(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        table_id = data.get('table_id')

        if not table_id:
            return JsonResponse({"success": False, "message": "Table ID is missing."}, status=400)

        with transaction.atomic():
            sid = transaction.savepoint()

            try:
                # All your database operations here
                today = date.today()
                counter, _ = DailyOrderCounter.objects.get_or_create(date=today)
                counter.counter += 1
                counter.save()
                display_id = f"{today.strftime('%Y%m%d')}-{counter.counter:03d}"

                items_to_invoice = OrderItem.objects.select_for_update().filter(
                    order__table_id=table_id,
                    invoice__isnull=True,
                    order__inHold=False,
                    order__order_status__name__in=['printed']
                )

                if not items_to_invoice.exists():
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({"success": False, "message": "No uninvoiced items found for this table."}, status=404)

                affected_order_ids = set(items_to_invoice.values_list('order_id', flat=True))
                total_amount = sum(item.price for item in items_to_invoice)

                invoice = Invoice.objects.create(
                    table_id=table_id,
                    total_amount=total_amount,
                    created_at=timezone.now(),
                    created_by=request.user,
                    display_id=display_id
                )

                items_updated = items_to_invoice.update(invoice=invoice)

                # CRITICAL: If this fails, raise an exception to trigger rollback
                try:
                    completed_status = OrderStatus.objects.get(name='completed')
                except OrderStatus.DoesNotExist:
                    # Don't return JsonResponse here - raise an exception instead
                    transaction.savepoint_rollback(sid)
                    raise ValueError("System error: 'completed' status not found.")

                orders_updated = 0
                for order_id in affected_order_ids:
                    if not OrderItem.objects.filter(order_id=order_id, invoice__isnull=True).exists():
                        updated_count = Order.objects.filter(id=order_id).update(order_status=completed_status)
                        orders_updated += updated_count

                transaction.savepoint_commit(sid)

                return JsonResponse({
                    "success": True,
                    "message": f"Invoice generated successfully for {items_updated} items.",
                    "invoice_id": invoice.id,
                    "orders_completed": orders_updated
                })

            except Exception as inner_e:
                transaction.savepoint_rollback(sid)
                raise inner_e  # Re-raise to trigger outer transaction rollback

    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=500)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"}, status=500)


@staff_member_required
@transaction.atomic
def generateInvoiceByItem(request):

    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        item_ids = data.get('item_ids', [])
        table_id = data.get('table_id') # You might not need the table_id if you get it from the items

        if not item_ids:
            return JsonResponse({"success": False, "message": "No items selected."}, status=400)
        with transaction.atomic():
            sid = transaction.savepoint()
            # Fetch the specific items to be invoiced
            items_to_invoice = OrderItem.objects.select_for_update().filter(id__in=item_ids, invoice__isnull=True, order__inHold=False, order__order_status__name__in=['printed'], order__table_id=table_id)

            today = date.today()
            counter, _ = DailyOrderCounter.objects.get_or_create(date=today)
            counter.counter += 1
            counter.save()
            display_id = f"{today.strftime('%Y%m%d')}-{counter.counter:03d}"
            if not items_to_invoice.exists():
                transaction.savepoint_rollback(sid)
                return JsonResponse({"success": False, "message": "Selected items are already invoiced or do not exist."}, status=404)
            # 1. Get the unique IDs of all parent orders that were affected.
            affected_order_ids = set(items_to_invoice.values_list('order_id', flat=True))

            # Calculate total and create the invoice
            total_amount = sum(item.price for item in items_to_invoice)
            invoice = Invoice.objects.create(
                table_id=items_to_invoice.first().order.table.id, # Get table_id from an item
                total_amount=total_amount,
                created_at=timezone.now(),
                created_by=request.user,
                display_id=display_id
            )

            # Link the items to the new invoice
            items_to_invoice.update(invoice=invoice)


            # 2. Get the 'completed' status object once.
            try:
                completed_status = OrderStatus.objects.get(name='completed')
            except OrderStatus.DoesNotExist:
                # This is a critical configuration error, so we stop the transaction.
                transaction.savepoint_rollback(sid)
                return JsonResponse({"success": False, "message": "System error: 'completed' status not found."}, status=500)

        # 3. Loop through each affected order and check its status.
            for order_id in affected_order_ids:
                # Check if the order has any OTHER items that are still uninvoiced.
                is_fully_invoiced = not OrderItem.objects.filter(order_id=order_id, invoice__isnull=True).exists()

                if is_fully_invoiced:
                    # If all items for this order are now invoiced, update its status.
                    Order.objects.filter(id=order_id).update(order_status=completed_status)

            transaction.savepoint_commit(sid)
            return JsonResponse({
                "success": True,
                "message": f"Invoice generated successfully for {len(item_ids)} items.",
                "invoice_id": invoice.id,
        })

    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@staff_member_required
def invoice_dashboard(request):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "message": "Invalid request method. Only GET requests are allowed."
        }, status=405)

    try:
        # Get all filter parameters from the URL
        table_id = request.GET.get('table_id')
        is_paid = request.GET.get('is_paid')
        start_date_str = request.GET.get("start_date") # This is the string 'YYYY-MM-DD' or None
        end_date_str = request.GET.get("end_date")     # This is the string 'YYYY-MM-DD' or None

        tables = Table.objects.all().order_by('id')
        invoices = Invoice.objects.filter(inHold=False).order_by('-created_at')

        # Apply table filter
        if table_id:
            invoices = invoices.filter(table_id=table_id)

        # Apply payment status filter
        if is_paid == 'true':
            invoices = invoices.filter(is_paid=True)
        elif is_paid == 'false':
            invoices = invoices.filter(is_paid=False)

        # Handle date filtering
        start_date = None
        end_date = None

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError as e:
            return JsonResponse({
                "success": False,
                "message": f"Invalid date format. Please use YYYY-MM-DD. Error: {str(e)}"
            }, status=400)

        if start_date and end_date:
            if start_date > end_date:
                return JsonResponse({"success": False, "message": "Start date cannot be after end date."}, status=400)
            invoices = invoices.filter(created_at__date__range=[start_date, end_date])
        elif start_date:
            invoices = invoices.filter(created_at__date__gte=start_date)
        elif end_date:
            invoices = invoices.filter(created_at__date__lte=end_date)

        # Apply pagination
        paginator = Paginator(invoices, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # --- THIS IS THE FIX ---
        # Pass the original STRING variables back to the template context.
        return render(request, 'invoice_dashboard.html', {
            'page_obj': page_obj,
            'tables': tables,
            'selected_table_id': table_id,
            'start_date_str': start_date_str, # Pass the string for the form value
            'end_date_str': end_date_str,     # Pass the string for the form value
            'is_paid': is_paid,
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"}, status=500)

@staff_member_required
def view_invoice(request, invoice_id):
    """
    Fetches an invoice and all its related orders, items, and extras efficiently
    for display on an 88mm receipt.
    """
    # 1. Fetch the invoice object.
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # 2. THE FIX: Fetch the related orders and pre-load all their children.
    # This is the most efficient way to get the data for the template.
    orders = invoice.orders.prefetch_related(
        'orderitem_set__orderitemextra_set' # For each order, get its items, and for each item, get its extras.
    ).all()
    print('orders : ',str(orders))
    # 3. Pass the invoice and the fully-loaded orders to the template.
    context = {
        'invoice': invoice,
        'orders': orders
    }

    return render(request, 'invoice.html', context)

@staff_member_required
def view_invoiceA4(request, invoice_id):
    """
    Fetches an invoice, then groups its items by type and extras,
    calculates quantities and subtotals, and renders them for display.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # 1. Fetch all items and their extras efficiently.
    items = invoice.order_items.prefetch_related('orderitemextra_set').all()

    # 2. THE GROUPING LOGIC
    # We will process the flat list of items into a grouped dictionary.
    grouped_items = {}

    for item in items:
        # Create a unique signature for the item based on its extras.
        # We sort the extras by name to ensure that [Cheese, Bacon] is the same as [Bacon, Cheese].
        extra_names = sorted([extra.extra_name for extra in item.orderitemextra_set.all()])

        # The signature combines the main item's ID and the sorted list of extra names.
        # e.g., "item_5-extra_Avocado-extra_Fries"
        signature = f"item_{item.item.id}-" + "-".join([f"extra_{name}" for name in extra_names])

        if signature not in grouped_items:
            # If this is the first time we've seen this combination, create a new entry.
            grouped_items[signature] = {
                'name': item.item_name,
                'unit_price': item.price, # The price of one unit with its extras
                'quantity': 0,
                'subtotal': 0,
                'extras': list(item.orderitemextra_set.all().values('extra_name', 'extra_price'))
            }

        # Increment the quantity and subtotal for this group.
        grouped_items[signature]['quantity'] += 1
        grouped_items[signature]['subtotal'] += item.price

    # 3. Pass the invoice and the *values* of the grouped_items dictionary to the template.
    context = {
        'invoice': invoice,
        'grouped_items': grouped_items.values() # The template will receive a list of these dictionaries
    }

    return render(request, 'invoiceA4.html', context)



@require_http_methods(["POST"])
@staff_member_required
def process_payment(request, invoice_id):
    """
    API endpoint to process a payment for a given invoice.
    Expects a JSON payload with 'amount', 'method', 'transaction_id' (optional), and 'notes' (optional).
    """
    try:
        # 1. Parse and validate incoming JSON data
        try:
            print('this is the data '+str(request.body))
            data = json.loads(request.body)
            amount = Decimal(str(data.get("amount")))
            method = data.get("method")
            transaction_id = data.get("transaction_id")
            notes = data.get("notes", "")
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)

        # Validate required fields
        if not all([amount, method]):
            return JsonResponse({"success": False, "error": "Amount and payment method are required"}, status=400)

        # Ensure amount is positive
        if amount <= 0:
            return JsonResponse({"success": False, "error": "Payment amount must be positive"}, status=400)

        with transaction.atomic():
            # 2. Retrieve and lock the invoice to prevent race conditions
            try:
                invoice = Invoice.objects.select_for_update().get(id=invoice_id)
            except Invoice.DoesNotExist:
                return JsonResponse({"success": False, "error": "Invoice not found"}, status=404)

            # 3. Validate payment against current balance
            # Refresh invoice to get the absolute latest balance_due before validation
            invoice.refresh_from_db()
            current_balance_due = invoice.balance_due
            if amount > current_balance_due:
                return JsonResponse({
                    "success": False,
                    "error": f"Payment amount ({amount}) exceeds remaining balance ({current_balance_due:.2f})"
                }, status=400)

            # 4. Create the payment record
            try:
                payment = Payment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    method=method,
                    transaction_id=transaction_id,
                    notes=notes,
                    processed_by=request.user
                )
            except Exception as e:
                # Log the exception for debugging purposes
                print(f"Error creating payment: {e}")
                return JsonResponse({"success": False, "error": f"Error creating payment: {str(e)}"}, status=500)

            # 5. Update invoice status (handled by Payment model's save method)
            # The Payment model's save method calls invoice.update_payment_status()
            # which then saves the invoice's is_paid and status fields.

            # Refresh the invoice instance AGAIN to get the latest calculated properties after payment and status update
            invoice.refresh_from_db()

            # 6. Prepare response data
            message = f"Partial payment received. Remaining balance: {invoice.balance_due:.2f} RWF"
            if invoice.is_fully_paid:
                message = "Payment processed successfully! Invoice is now fully paid."

            return JsonResponse({
                "success": True,
                "payment_id": payment.id,
                "amount_paid": float(invoice.amount_paid), # Total amount paid for this invoice
                "balance_due": float(invoice.balance_due),
                "is_fully_paid": invoice.is_fully_paid,
                "status": invoice.status,
                "message": message
            })

    except Exception as e:
        # Catch any unexpected errors and return a generic error response
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)


@staff_member_required
def mark_unpaid(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            invoice_id = data.get('invoice_id')
            reason = data.get('reason')

            if not reason:
                return JsonResponse({'success': False, 'message': 'Reason is required.'})

            invoice = Invoice.objects.get(id=invoice_id)

            # Store the reason and user
            UnpaidReasonLog.objects.create(
                invoice=invoice,
                user=request.user,
                reason=reason
            )

            # Soft-delete the last payment
            last_payment = Payment.objects.filter(invoice=invoice, inHold=False).last()
            if last_payment:
                last_payment.inHold = True
                last_payment.save()

            # Optionally update invoice status
            invoice.status = "Unpaid"
            invoice.is_paid = False
            invoice.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@require_http_methods(["POST"])
@staff_member_required
def update_invoice_status(request, invoice_id):
    try:
        data = json.loads(request.body)
        is_paid = data.get('is_paid')

        with transaction.atomic():
            invoice = Invoice.objects.select_for_update().get(id=invoice_id)

            if is_paid and not invoice.is_paid:
                # If marking as paid, create a payment for the remaining balance
                if invoice.balance_due > 0:
                    Payment.objects.create(
                        invoice=invoice,
                        amount=invoice.balance_due,
                        method='CASH',  # Default method
                        processed_by=request.user,
                        notes='Marked as paid via status change'
                    )
                invoice.is_paid = True
                invoice.status = 'paid'
            elif not is_paid and invoice.is_paid:
                # If marking as unpaid, you might want to void the last payment
                # or handle this differently based on your business logic
                invoice.is_paid = False
                invoice.status = 'pending'

            invoice.save()

            return JsonResponse({
                'success': True,
                'is_paid': invoice.is_paid,
                'status': invoice.status
            })

    except Invoice.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invoice not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
def print_invoice_view(request, invoice_id):
    """
    Fetches an invoice, then groups its items by type and extras,
    calculating quantities and subtotals for a compact 88mm receipt.
    """
    # 1. Get the invoice object.
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # 2. Fetch all individual items and their extras efficiently.
    items = invoice.order_items.prefetch_related('orderitemextra_set').all()

    # 3. THE GROUPING LOGIC
    # This dictionary will store the aggregated items.
    grouped_items = {}

    for item in items:
        # Create a unique signature for the item based on its extras.
        # We sort the extras by name to ensure the order doesn't matter.
        extra_names = sorted([extra.extra_name for extra in item.orderitemextra_set.all()])

        # The signature combines the main item's ID and the sorted list of extra names.
        # e.g., "item_5-extra_Avocado-extra_Fries"
        signature = f"item_{item.item.id}-" + "-".join([f"extra_{name}" for name in extra_names])

        if signature not in grouped_items:
            # If this is the first time we've seen this combination, create a new entry.
            grouped_items[signature] = {
                'name': item.item_name,
                'unit_price': item.price, # The price of a single unit with its extras
                'quantity': 0,
                'subtotal': 0,
                'extras': list(item.orderitemextra_set.all().values('extra_name', 'extra_price'))
            }

        # For every item that matches this signature, increment the quantity and subtotal.
        grouped_items[signature]['quantity'] += 1
        grouped_items[signature]['subtotal'] += item.price

    # 4. Prepare the context for the template.
    # We pass the invoice and the list of grouped item dictionaries.
    context = {
        'invoice': invoice,
        'grouped_items': grouped_items.values()
    }

    return render(request, 'print_invoice.html', context)
