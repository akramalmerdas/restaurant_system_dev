from decimal import Decimal
from django.utils import timezone
from django.utils.timezone import now
from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse, JsonResponse,HttpResponseForbidden
from django.urls import reverse
from menu.models import Item, Extra
from orders.models import Order, OrderItem, OrderItemExtra, OrderStatus, DailyOrderCounter
from users.models import Customer, Staff
from reservations.models import Table
from payments.models import Invoice, Payment, UnpaidReasonLog
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum ,Count, Avg,Prefetch,OuterRef, Subquery,DecimalField,F,Value,Q
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from datetime import datetime ,date, time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
from core.decorators import staff_member_required, admin_required

def orderPage(request, menu_item_id):
    item = get_object_or_404(Item, id=menu_item_id)
    return render(request, 'meal_page.html', {'item': item})

def get_extras(request, menu_item_id):
  try:
      item = Item.objects.get(id=menu_item_id)
      extras = item.extras.all()
      extras_list = [{'id':extra.id,'name': extra.name, 'price': float(extra.price)} for extra in extras]
      return JsonResponse({'extras': extras_list})
  except Item.DoesNotExist:
      return JsonResponse({'error': 'Item not found'}, status=404)

def orderDetails(request):
    order_items = request.session.get('order', [])
    if not order_items:
        return render(request, 'order_page.html', {'message': 'Your order is empty.'})

    formatted_order_items = []
    total_amount = 0
    for item in order_items:
        extras = item.get('extras', [])
        extra_price = sum(extra['price'] for extra in extras)
        subtotal =item['subtotal']
        formatted_order_items.append({
            'item_id':item['item_id'],
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['price'],
            'extras': json.dumps([{'id': extra['id'], 'name': extra['name']} for extra in extras]) if extras else '[]',
            'extras_names': ', '.join(extra['name'] for extra in extras) if extras else 'None',
            'extra_price': extra_price,
            'subtotal': subtotal,
            'table':item['table'],
            'row': item['row']
        })
        total_amount += subtotal
        total_amount = round(total_amount, 2)

    return render(request, 'order_page.html', {
        'order_items': formatted_order_items,
        'total_amount': total_amount,
        'tables': Table.objects.all()
    })

def orderDetailApi(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = []
    for item in order.orderitem_set.all():
        order_items.append({
            'id': item.id,
            'name': str(item.item_name),
            'price': str(item.item_price),
            'total': str(item.price),
        })
    data = {
        'id': order.id,
        'table_number': order.table_number,
        'total_amount': str(order.total_amount),
        'deleted_by': str(order.deleted_by) if order.deleted_by else 'System',
        'deleted_reason': order.deleted_reason,
        'deleted_at': order.deleted_at.isoformat() if order.deleted_at else None,
        'ordered_at': order.ordered_at.isoformat(),
        'order_items': order_items
    }
    return JsonResponse(data)

def orderView(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.prefetch_related('selected_extras').all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_view.html', context)

def orderList(request):
  orders = Order.objects.prefetch_related('orderitem_set__item__extras').all()
  return render(request, 'order_list.html', {'orders': orders})

def addToOrder(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data['item_id']
        quantity = data['quantity']
        notes = data.get('notes', '')
        extras_data = data['extras']

        item = Item.objects.get(id=item_id)
        extras = []
        for extra_data in extras_data:
            extra_instance = Extra.objects.get(id=extra_data['id'])
            extras.append(extra_instance)

        order = request.session.get('order', [])
        item_price = float(item.price)
        has_extras_in_db = item.extras.exists()

        if not has_extras_in_db and not extras_data:
            for existing_item in order:
                if existing_item['item_id'] == item.id and not existing_item.get('extras'):
                    existing_item['quantity'] += quantity
                    existing_item['subtotal'] = existing_item['price'] * existing_item['quantity']
                    request.session['order'] = order
                    return JsonResponse({"status": "success", "message": "Item quantity updated"})

        row_number = len(order)
        order_item = {
         'row': row_number,
         'item_id': item.id,
         'name': item.name,
         'quantity': quantity,
         'price': item_price,
         'customizations': notes,
         'extras': [
                {
                    'id': extra.id,
                    'name': extra.name,
                    'price': float(extra.price),
                    'quantity': extra_data['quantity']
                }
                for extra, extra_data in zip(extras, extras_data)
            ],
         'subtotal': item_price * quantity + sum(float(extra.price) * extra_data['quantity'] for extra, extra_data in zip(extras, extras_data)),
         'table':'table1'
        }
        order.append(order_item)
        request.session['order'] = order
        return JsonResponse({"status": "success", "message": "Item added to order"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def delete_order_item(request, item_id):
    order_items = request.session.get('order', [])
    item_to_delete = None
    for item in order_items:
        if item['row'] == item_id:
            item_to_delete = item
            break
    if item_to_delete:
        order_items.remove(item_to_delete)
        request.session['order'] = order_items
    return redirect('orders:orderDetails')

def updateOrderItem(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        extras_raw = request.POST.get('extras', '')
        notes = request.POST.get('notes', '')
        row = request.POST.get('row', '')
        order = request.session.get('order', [])
        for item in order:
            if str(item['row']) == str(row) and item_id == str(item['item_id']):
                item['quantity'] = quantity
                item['customizations'] = notes
                if extras_raw:
                    extras = []
                    for extra_id in extras_raw.split(','):
                        extra_id = extra_id.strip()
                        if not extra_id or not extra_id.isdigit():
                            continue
                        try:
                            extra_obj = Extra.objects.get(id=int(extra_id))
                            extras.append({
                                'id': extra_obj.id,
                                'name': extra_obj.name,
                                'price': float(extra_obj.price),
                                'quantity': 1
                            })
                        except Extra.DoesNotExist:
                            continue
                    item['extras'] = extras
                extras_for_calc = item.get('extras', [])
                item['subtotal'] = item['price'] * quantity + sum(
                    extra.get('price', 0) * quantity for extra in extras_for_calc
                )
                break
        request.session['order'] = order
        return redirect('orders:orderDetails')
    return redirect('orders:orderDetails')

def emptyOrder(request):
    if 'order' in request.session:
        request.session.pop('order', None)
        request.session.modified = True
    return JsonResponse({"status": "success", "message": "Cart was emptied successfully."})

@transaction.atomic
def submitOrder(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)
    order_data = request.session.get('order', [])
    if not order_data:
        return JsonResponse({"status": "error", "message": "Your cart is empty."}, status=400)
    try:
        pending_status = OrderStatus.objects.get(name__iexact='pending')
    except OrderStatus.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Order status 'pending' not found."}, status=500)
    table_number = request.session.get('table_number')
    try:
        orderTable = Table.objects.get(number=table_number) if table_number else Table.objects.get(number='Take Away')
    except Table.DoesNotExist:
        return JsonResponse({"status": "error", "message": f"Table '{table_number or 'Take Away'}' not found."}, status=400)
    today = date.today()
    counter, _ = DailyOrderCounter.objects.get_or_create(date=today)
    counter.counter += 1
    counter.save()
    display_id = f"{today.strftime('%Y%m%d')}-{counter.counter:03d}"
    customer = None
    staff_waiter = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            pass
        try:
            staff_waiter = Staff.objects.get(user=request.user)
        except Staff.DoesNotExist:
            pass
    order = Order.objects.create(
        customer=customer,
        waiter=staff_waiter,
        order_status=pending_status,
        total_amount=0,
        table=orderTable,
        table_number=orderTable.number,
        display_id=display_id
    )
    orderTable.status = 'occupied'
    orderTable.save()
    total_order_amount = 0
    for item_data in order_data:
        try:
            item = Item.objects.get(id=item_data['item_id'])
            extras_list_data = item_data.get('extras', [])
        except Item.DoesNotExist:
            continue
        for _ in range(item_data['quantity']):
            order_item = OrderItem.objects.create(
                order=order,
                item=item,
                item_name=item.name,
                item_price=item.price,
                price=item.price,
                customizations=item_data.get('customizations', '')
            )
            for extra_data in extras_list_data:
                try:
                    extra = Extra.objects.get(id=extra_data['id'])
                    OrderItemExtra.objects.create(
                        order_item=order_item,
                        extra=extra,
                        quantity=1,
                        extra_name=extra.name,
                        extra_price=extra.price
                    )
                except Extra.DoesNotExist:
                    continue
            order_item.save()
            total_order_amount += order_item.price
    order.total_amount = total_order_amount
    order.save(update_fields=["total_amount"])
    request.session['order'] = []
    request.session.pop('table_number', None)
    if staff_waiter and staff_waiter.role.lower() == 'manager':
        redirect_url = reverse('orders:admin_dashboard')
    else:
        redirect_url = reverse('reservations:table_landing_page')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "admin_notifications",
        {
            "type": "order_notification",
            "order_id": order.id,
            "customer": order.customer.user.username if customer and customer.user else "Guest",
            "total": str(order.total_amount),
            "timestamp": timezone.now().isoformat(),
            "redirect_url": redirect_url,
        }
    )
    return JsonResponse({
        "status": "success",
        "message": "Order submitted successfully!",
        "redirect_url": redirect_url
    })

def printOrder(request):
    order_items = request.session.get('order', [])
    if not order_items:
        return JsonResponse({"status": "error", "message": "Your order is empty."}, status=400)
    formatted_order_items = []
    total_amount = 0
    for item in order_items:
        extras = item.get('extras', [])
        extra_price = sum(extra['price'] for extra in extras)
        subtotal =item['subtotal']
        formatted_order_items.append({
            'item_id':item['item_id'],
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['price'],
            'extras': extras if extras else 'None',
            'extra_price': extra_price,
            'subtotal': subtotal,
            'table':item['table']
        })
        total_amount += subtotal
        total_amount = round(total_amount, 2)
    return JsonResponse({
        'order_items': formatted_order_items,
        'total_amount': total_amount
    })

@staff_member_required
def adminDashboard(request):
    tables = Table.objects.all().order_by('id')
    selected_table_id = request.GET.get('table_id')
    status_filter = request.GET.get('status')
    orders = Order.objects.filter(inHold=False).order_by('-ordered_at')
    if selected_table_id:
        orders = orders.filter(table__id=selected_table_id)
    if status_filter:
        if status_filter == 'cancelled':
            orders = orders.filter(order_status__name='cancelled')
        elif status_filter == 'non_cancelled':
            orders = orders.exclude(order_status__name='cancelled')
        else:
            orders = orders.filter(order_status__name=status_filter)
    status_counts = {
        'all': orders.count(),
        'pending': orders.filter(order_status__name='pending').count(),
        'completed': orders.filter(order_status__name='completed').count(),
        'served': orders.filter(order_status__name='served').count(),
        'cancelled': orders.filter(order_status__name='cancelled').count(),
    }
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_dashboard.html', {
        'tables': tables,
        'page_obj': page_obj,
        'orders': orders,
        'selected_table_id': selected_table_id,
        'selected_status': status_filter,
        'status_counts': status_counts,
    })

@staff_member_required
def deleteOrder(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = get_object_or_404(Order, id=order_id)
            order.inHold = True
            order.deleted_at = timezone.now()
            order.deleted_by = request.user
            order.deleted_reason = data.get('reason', '')
            order.save()
            return JsonResponse({
                "success": True,
                "message": "Order cancelled successfully!"
            })
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method. Use POST."}, status=405)

@staff_member_required
def update_order_status(request, order_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            statues = data.get("status")
            if statues == 'Pending':
                new_status_name = 'pending'
            elif statues == 'Ready to Print':
                new_status_name = 'readytoprint'
            elif statues == 'Printed':
                new_status_name = 'printed'
            elif statues == 'Served':
                new_status_name = 'served'
            elif statues == 'Delivered':
                new_status_name = 'delivered'
            elif statues == 'Completed':
                new_status_name = 'completed'
            elif statues == 'Printing':
                new_status_name = 'printing'
            order = get_object_or_404(Order, id=order_id)
            new_status = get_object_or_404(OrderStatus, name=new_status_name)
            order.order_status = new_status
            order.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})

@staff_member_required
def cancelled_orders(request):
    table_number = request.GET.get('table_number')
    date = request.GET.get('date')
    cancelled_orders_queryset = Order.objects.filter(inHold=True).select_related(
        'customer', 'deleted_by', 'table'
    ).order_by('-deleted_at')
    if table_number:
        cancelled_orders_queryset = cancelled_orders_queryset.filter(table__number=table_number)
    if date:
        cancelled_orders_queryset = cancelled_orders_queryset.filter(deleted_at__date=date)
    total_cancelled_orders = cancelled_orders_queryset.count()
    total_cancelled_amount = cancelled_orders_queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    avg_cancellation_amount = cancelled_orders_queryset.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
    paginator = Paginator(cancelled_orders_queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    tables = Table.objects.all().values_list('number', flat=True).distinct()
    order_dates = Order.objects.filter(inHold=True).exclude(
        deleted_at__isnull=True
    ).dates('deleted_at', 'day').distinct()
    context = {
        'cancelled_orders': page_obj,
        'tables': tables,
        'order_dates': order_dates,
        'selected_table': table_number,
        'selected_date': date,
        'page_title': 'Cancelled Orders',
        'total_cancelled_orders': total_cancelled_orders,
        'total_cancelled_amount': total_cancelled_amount,
        'avg_cancellation_amount': avg_cancellation_amount,
        'page_obj': page_obj,
    }
    return render(request, 'deleted_orders.html', context)

@staff_member_required
def print_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    csrf_token = get_token(request)
    if request.method == "POST":
        try:
            printed_status = OrderStatus.objects.get(name="printed")
            pending_status = OrderStatus.objects.get(name="pending")
            if order.order_status == pending_status:
              order.order_status = printed_status
            order.printed_at = timezone.now()
            order.save()
            return JsonResponse({"success": True, "message": "Print confirmed."})
        except OrderStatus.DoesNotExist:
            return JsonResponse({"success": False, "message": "Printed status not found."}, status=500)
    items = order.orderitem_set.prefetch_related('orderitemextra_set').all()
    grouped_items = {}
    for item in items:
        extra_names = sorted([extra.extra_name for extra in item.orderitemextra_set.all()])
        custom_note = item.customizations.strip().lower() if item.customizations else ""
        signature = f"item_{item.item.id}-note_{custom_note}-" + "-".join([f"extra_{name}" for name in extra_names])
        if signature not in grouped_items:
            grouped_items[signature] = {
                'name': item.item.name,
                'customizations': item.customizations,
                'unit_price': item.price,
                'quantity': 1,
                'extras': list(item.orderitemextra_set.all().values('extra_name', 'extra_price')),
            }
        else:
            grouped_items[signature]['quantity'] += 1
    return render(request, 'print_order.html', {
        'order': order,
        'order_id': order_id,
        'csrf_token': csrf_token,
        'grouped_items': grouped_items.values()
    })
