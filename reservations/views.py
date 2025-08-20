from django.shortcuts import redirect, render , get_object_or_404
from django.http import JsonResponse
from .models import Table
from orders.models import Order, OrderItem
from django.core import serializers
from django.db import transaction
from core.decorators import staff_member_required
from django.db.models import Prefetch
import json

def setTableNumber(request):
    print ('we enterd the set table number function')
    if request.method == 'POST':
        print ('we enterd the post method')
        table_number = request.POST.get('table_number')
        if table_number:
            request.session['table_number'] = table_number
            print('this is the table number '+ str(table_number))
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@staff_member_required
def table_dashboard(request):
    """View for managing restaurant tables"""
    if request.method == "POST":
        # Handle table creation
        number = request.POST.get('number')
        capacity = request.POST.get('capacity')
        location = request.POST.get('location')

        Table.objects.create(
            number=number,
            capacity=capacity,
            location=location,
            status='available'
        )
        return redirect('table_dashboard')

    # Get all tables and their stats
    tables = Table.objects.all().order_by('number')
    total_tables = tables.count()
    available_tables = tables.filter(status='available').count()
    occupied_tables = tables.filter(status='occupied').count()
    reserved_tables = tables.filter(status='reserved').count()

    context = {
        'tables': tables,
        'total_tables': total_tables,
        'available_tables': available_tables,
        'occupied_tables': occupied_tables,
        'reserved_tables': reserved_tables,
    }

    return render(request, 'table_dashboard.html', context)

def tableLanding(request):
    tables = Table.objects.filter(inHold=False).order_by('section', 'number')
    tables_json = serializers.serialize('json', tables)
    print('this is the tables count'+str(tables.count))
    return render(request, 'tables_landing_page.html', {'tables_json': tables_json})

@staff_member_required
def update_table_status(request, table_id):
    """Update table status via AJAX"""
    if request.method == "POST":
        try:
            table = Table.objects.get(id=table_id)
            status = request.POST.get('status')
            if status in ['available', 'occupied', 'reserved']:
                table.status = status
                table.save()
                return JsonResponse({'status': 'success'})
        except Table.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
def delete_table(request, table_id):
    """Delete a table"""
    if request.method == "POST":
        try:
            table = Table.objects.get(id=table_id)
            table.delete()
            return JsonResponse({'status': 'success'})
        except Table.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
def edit_table(request, table_id):
    if request.method == 'POST':
        try:
            table = Table.objects.get(id=table_id)
            data = json.loads(request.body)
            table.number = data.get('number', table.number)
            table.capacity = data.get('capacity', table.capacity)
            table.status = data.get('status', table.status)
            table.save()
            return JsonResponse({
                'success': True,
                'table': {
                    'id': table.id,
                    'number': table.number,
                    'capacity': table.capacity,
                    'status': table.status,
                }
            })
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Table not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@staff_member_required
def get_table_history(request, table_id):
    print('here we entered the table history view ')
    try:
        table = Table.objects.get(id=table_id)
        # Get the last 10 orders for this table
        orders = Order.objects.filter(table=table).order_by('ordered_at')[:10]

        print(orders)
        history = []
        for order in orders:
            history.append({
                'order_id': order.id,
                'status': order.order_status.name,
                'total': float(order.total_amount),
                'ordered_at': order.ordered_at.strftime('%Y-%m-%d %H:%M'),
                'items_count': order.orderitem_set.count()
            })
        print('here we are printitng the history ')
        print(history)
        return JsonResponse({'success': True, 'history': history})
    except Table.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Table not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@staff_member_required
def getOrderByTable(request, table_id):
    """
    This view fetches all uninvoiced orders for a specific table,
    calculates a summary, and renders the waiter's order management page.
    It is designed to work perfectly with the provided waiter_orders.html template.
    """

    try:
        tables = Table.objects.all().order_by('id')
        table = Table.objects.get(id=table_id)
    except Table.DoesNotExist:
        return render(request, 'error_page.html', {'message': 'Table not found.'}, status=404)

    # 1. EFFICIENTLY FETCH DATA
    # This is the most critical part. We fetch all orders and their related,
    # uninvoiced items and extras in just a few database queries.
    orders_queryset = Order.objects.filter(
        table=table,
        order_status__name__in=['printed'],
        inHold=False
    ).prefetch_related(
        # Use a Prefetch object to get ONLY the uninvoiced items for each order.
        Prefetch(
            'orderitem_set',
            queryset=OrderItem.objects.filter(invoice__isnull=True),
            to_attr='uninvoiced_items' # Store these filtered items in a custom attribute
        ),
        # For those specific uninvoiced items, prefetch their extras.
        'uninvoiced_items__orderitemextra_set'
    ).distinct().order_by('ordered_at')

    # 2. PREPARE DATA AND CALCULATE SUMMARY
    # Now we loop through the results in Python to build the final context.
    # This is fast because all database queries are already done.
    final_orders_list = []
    final_total_amount = 0
    total_items_count = 0

    for order in orders_queryset:
        # The 'uninvoiced_items' attribute exists on each order because of our Prefetch object.
        if hasattr(order, 'uninvoiced_items') and order.uninvoiced_items:
            # This order has items to display, so we add it to our final list.
            final_orders_list.append(order)

            # Calculate totals based only on the items we are displaying.
            for item in order.uninvoiced_items:
                total_items_count += 1
                final_total_amount += item.price

    # 3. CREATE THE FINAL CONTEXT
    context = {
        'tables': tables,
        'table': table,
        'orders': final_orders_list, # Pass the filtered list of order objects
        'summary': {
            'total_orders': len(final_orders_list),
            'total_items': total_items_count,
            'final_total': final_total_amount
        },
        'waiter': request.user if request.user.is_authenticated else None
    }

    return render(request, 'waiter_orders.html', context)

@staff_member_required
def moveTable(request):
    print('we enterd the move table function')
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    """
    Transfer specified orders to a target table
    Accepts a list of order IDs - can be one order, multiple orders, or all orders from a table
    """
    try:
        # Get data from POST request
        data = json.loads(request.body)
        order_ids = data.get('order_select', [])  # List of order IDs to transfer
        target_table_id = data.get('target_table_id')

        # Validate input
        if not order_ids:
            return JsonResponse({
                "success": False,
                "message": "No orders selected for transfer"
            }, status=400)

        if not target_table_id:
            return JsonResponse({
                "success": False,
                "message": "Target table ID is required"
            }, status=400)

        # Ensure order_ids is a list
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        # Get target table
        target_table = get_object_or_404(Table, id=target_table_id)

        # Get orders to transfer
        orders_to_transfer = Order.objects.filter(
            id__in=order_ids,
            inHold=False  # Only active orders
        )

        if not orders_to_transfer.exists():
            return JsonResponse({
                "success": False,
                "message": "No valid orders found for transfer"
            }, status=404)

        # Check if any orders are already on the target table


        already_on_target = orders_to_transfer.filter(table=target_table)
        if already_on_target.exists():
            already_on_target_ids = list(already_on_target.values_list('id', flat=True))
            return JsonResponse({
                "success": False,
                "message": f"Orders {already_on_target_ids} are already on table {target_table.table_number}"
            }, status=400)

        # Transfer orders with transaction for data integrity
        with transaction.atomic():
            transferred_orders = []
            source_tables = set()  # Track source tables for response message

            for order in orders_to_transfer:
                # Store current table info for history
                current_table_number = order.table_number
                source_tables.add(current_table_number)

                # Store previous table information
                if order.previous_table:
                    # Append to existing previous table history
                    order.previous_table += f" -> {current_table_number}"
                else:
                    # First time moving, store the original table
                    order.previous_table = current_table_number

                # Update table assignment
                order.table = target_table
                order.table_number = target_table.number
                order.save()
                print('this is the order ids '+ str(order_ids))
                print('this is the target table id '+ str(current_table_number))
                transferred_orders.append({
                    'id': order.id,
                    'display_id': order.display_id,
                    'previous_table': current_table_number,
                    'new_table': target_table.number
                })

        # Create response message
        transferred_count = len(transferred_orders)
        source_tables_str = ", ".join(source_tables)

        if transferred_count == 1:
            message = f"Successfully transferred 1 order from {source_tables_str} to {target_table.number}"
        else:
            message = f"Successfully transferred {transferred_count} orders from {source_tables_str} to {target_table.number}"

        return JsonResponse({
            "success": True,
            "message": message,
            "transferred_count": transferred_count,
            "target_table": target_table.number,
            "transferred_orders": transferred_orders
        })

    except Table.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Target table not found"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"An error occurred: {str(e)}"
        }, status=500)
