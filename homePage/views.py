from decimal import Decimal
from django.utils import timezone
from django.utils.timezone import now
from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from item.models import Item ,Order,OrderItem,Extra,OrderItemExtra,OrderStatus,Customer,Table,Invoice,Staff,Payment,UnpaidReasonLog,DailyOrderCounter
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum ,Count, Avg,Prefetch,OuterRef, Subquery,DecimalField,F,Value
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
from datetime import datetime ,date, time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers
from django.views.decorators.http import require_http_methods
# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.core.paginator import Paginator
from collections import defaultdict
from django.db.models.functions import Coalesce

@login_required
def index(request):
    # Fetch table_id from the query parameter
    table_number = request.GET.get('table_id')
    # table = None

    # If table_id is provided, fetch the table object
    if table_number:
        try:
          
            request.session['table_number'] = table_number

        except Table.DoesNotExist:
            table_number = None  # Handle invalid table_id gracefully

    # Fetch menu items as usual
    lunchItems = Item.objects.filter(category__id=3)
    saladItems = Item.objects.filter(category__id=8)
    drinks = Item.objects.filter(category__id=13)
    sweets= Item.objects.filter(category__id=12)
    breakFast = Item.objects.filter(category__id=1)
    extras = Item.objects.filter(category__id=14)
    yemeni_sweets = Item.objects.filter(category__id=6)
    smoothie_bowls = Item.objects.filter(category__id=2)
    burgers = Item.objects.filter(category__id=11)
    dips = Item.objects.filter(category__id=9)
    soups = Item.objects.filter(category__id=10)
    sandwiches = Item.objects.filter(category__id=7)
    pots = Item.objects.filter(category__id=4)
    bowls = Item.objects.filter(category__id=5)
    user = request.user

    # Pass the table object to the template
    return render(request, 'index.html', {
        'lunch': lunchItems,
        'salad': saladItems,
        'drinks': drinks,
        'sweets': sweets,
        'breakFast': breakFast,
        'extra': extras,
        'yemeni_sweets': yemeni_sweets,
        'smoothie_bowls': smoothie_bowls,
        'burgers': burgers,
        'dips': dips,
        'soups': soups,
        'sandwiches': sandwiches,
        'pots': pots,
        'bowls': bowls,
        'user': user
      #  'table': table,  # Include the table in the context
    })






def orderPage(request, menu_item_id):  
    item = get_object_or_404(Item, id=menu_item_id)

    return render(request, 'meal_page.html', {'item': item})


def get_extras(request, menu_item_id):
  try:
        # Get the item by its ID
      item = Item.objects.get(id=menu_item_id)
        
        # Retrieve all related extras for the item
      extras = item.extras.all()  # Assuming a ManyToMany relation `extras` is defined in Item
        
        # Create a list of extras with their names and prices
      extras_list = [{'id':extra.id,'name': extra.name, 'price': float(extra.price)} for extra in extras]
        
      return JsonResponse({'extras': extras_list})
    
  except Item.DoesNotExist:
      return JsonResponse({'error': 'Item not found'}, status=404)


############################################ order details ####################
# def orderDetails(request):
#     # Fetch the order items from the session
#     order_items = request.session.get('order', [])
  
    
#     # If there are no items in the session, display a message
#     if not order_items:
#         return render(request, 'order_page.html', {'message': 'Your order is empty.'})

#     # Prepare the data for rendering
#     formatted_order_items = []
#     total_amount = 0  # Initialize total amount

#     for item in order_items:
#         # Fetch extras and their prices for each item
#         extras = item.get('extras', [])
#         extra_price = sum(extra['price'] for extra in extras)  # Calculate total price of extras

#         subtotal =item['subtotal'] # Calculate subtotal for each item
#         formatted_order_items.append({
#             'item_id':item['item_id'],
#             'name': item['name'],
#             'quantity': item['quantity'],
#             'unit_price': item['price'],
#             # Send extras as JSON string (id and name)
#             'extras': json.dumps([{'id': extra['id'], 'name': extra['name']} for extra in extras]) if extras else '[]',
#             'extras_names': ', '.join(extra['name'] for extra in extras) if extras else 'None',  # <-- add this line
#             'extra_price': extra_price,
#             'subtotal': subtotal,
#             'table':item['table']
             
#         })

#         # Add to the total amount
#         total_amount += subtotal
#         total_amount = round(total_amount, 2)

#     # Render the page with order items and total amount
#     return render(
#         request, 
#         'order_page.html', 
#         {
#             'order_items': formatted_order_items,
#             'total_amount': total_amount,
#        
#         }
#     )

###############################################order details waiter edition ###################################
def orderDetails(request):
    # Fetch the order items from the session
    order_items = request.session.get('order', [])
  
    
    # If there are no items in the session, display a message
    if not order_items:
        return render(request, 'order_page.html', {'message': 'Your order is empty.'})

    # Prepare the data for rendering
    formatted_order_items = []
    total_amount = 0  # Initialize total amount

    for item in order_items:
        # Fetch extras and their prices for each item
        extras = item.get('extras', [])
        extra_price = sum(extra['price'] for extra in extras)  # Calculate total price of extras

        subtotal =item['subtotal'] # Calculate subtotal for each item
        formatted_order_items.append({
            'item_id':item['item_id'],
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['price'],
            # Send extras as JSON string (id and name)
            'extras': json.dumps([{'id': extra['id'], 'name': extra['name']} for extra in extras]) if extras else '[]',
            'extras_names': ', '.join(extra['name'] for extra in extras) if extras else 'None',  # <-- add this line
            'extra_price': extra_price,
            'subtotal': subtotal,
            'table':item['table'],
            'row': item['row'] 
             
        })

        # Add to the total amount
        total_amount += subtotal
        total_amount = round(total_amount, 2)

    # Render the page with order items and total amount
    return render(
        request, 
        'order_page.html', 
        {
            'order_items': formatted_order_items,
            'total_amount': total_amount,
            'tables': Table.objects.all() 
        }
    )

################################### order Details api ###
def orderDetailApi(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    order_items = []
    for item in order.orderitem_set.all():
      
        order_items.append({
            'name': str(item.item_name),
            # 'quantity': item.quantity,
            'price': str(item.item_price),
            'total': str(item.price),
    
        })
        
    data = {
        'id': order.id,
        'table_number': order.table_number,
        'total_amount': str(order.total_amount),
        'deleted_by': order.deleted_by.get_full_name() if order.deleted_by else 'System',
        'deleted_reason': order.deleted_reason,
        'deleted_at': order.deleted_at.isoformat() if order.deleted_at else None,
        'ordered_at': order.ordered_at.isoformat(),
        'order_items': order_items
    }
    return JsonResponse(data)


def orderView(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.prefetch_related('selected_extras').all()  # Retrieve order items with their extras

    context = {
        'order': order,
        'order_items': order_items,
    }
   
    return render(request, 'order_view.html', context)


def orderList(request):
  orders = Order.objects.prefetch_related('orderitem_set__item__extras').all()
  return render(request, 'order_list.html', {'orders': orders})





@csrf_exempt
def addToOrder(request): 
    if request.method == "POST":
        # Parse incoming data
        data = json.loads(request.body)
        item_id = data['item_id']
        quantity = data['quantity']
        notes = data.get('notes', '')
        extras_data = data['extras']

        # Fetch item and extras from the database
        item = Item.objects.get(id=item_id)
        extras = []
        for extra_data in extras_data:
            extra_instance = Extra.objects.get(id=extra_data['id'])
            extras.append(extra_instance)

        # Get the existing order from the session (if it exists), or create an empty order if not
        order = request.session.get('order', [])

        # Convert item price (Decimal) to float for JSON serialization
        item_price = float(item.price)

        # Check if the item has any extras associated with it in the database
        has_extras_in_db = item.extras.exists()

        # If the item doesn't have extras in the database and no extras were selected
        if not has_extras_in_db and not extras_data:
            # Check if the item is already in the order
            for existing_item in order:
                if existing_item['item_id'] == item.id and not existing_item.get('extras'):
                    # Item already exists without extras, just update the quantity
                    existing_item['quantity'] += quantity
                    # Update the subtotal
                    existing_item['subtotal'] = existing_item['price'] * existing_item['quantity']
                    # Save the updated order to the session
                    request.session['order'] = order
                    return JsonResponse({"status": "success", "message": "Item quantity updated"})
        
        # Create a new order item structure (for items with extras or new items)
       
        row_number = len(order)
        print('this is the row number ' + str(row_number))
        order_item = {
         'row': row_number,
         'item_id': item.id,
         'name': item.name,
         'quantity': quantity,
         'price': item_price,  # Store the price as a float
         'customizations': notes,
         'extras': [
                {
                    'id': extra.id,
                    'name': extra.name,
                    'price': float(extra.price),  # Convert extra price to float
                    'quantity': extra_data['quantity']
                }
                for extra, extra_data in zip(extras, extras_data)
            ],
         'subtotal': item_price * quantity + sum(float(extra.price) * extra_data['quantity'] for extra, extra_data in zip(extras, extras_data)),  # Calculate subtotal with float values
         'table':'table1'      
        }

        # Add the new order item to the session order list
        order.append(order_item)
        print (str(order_item))
        # Save the updated order to the session
        request.session['order'] = order

        return JsonResponse({"status": "success", "message": "Item added to order"})
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




def delete_order_item(request, item_id):
    # Check if 'order_items' exists in the session
    order_items = request.session.get('order', [])
    # Find the item in the session
    item_to_delete = None
    for item in order_items:
        if item['row'] == item_id:  # Match the item by its ID
            item_to_delete = item
            break

    # If the item is found in the session, remove it
    if item_to_delete:
        order_items.remove(item_to_delete)
        request.session['order'] = order_items 
       # Save the updated list back to the session
      
    # print(request.session.get('order', []))
    # Redirect back to the order review page
    return redirect('orderDetails')  

######################### update order ######################################

@csrf_exempt
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
                # Only update extras if provided
                if extras_raw:
                    extras = []
                    for extra_id in extras_raw.split(','):
                        extra_id = extra_id.strip()
                        # Skip empty or invalid IDs
                        if not extra_id or not extra_id.isdigit():
                            continue
                        try:
                            extra_obj = Extra.objects.get(id=int(extra_id))
                            extras.append({
                                'id': extra_obj.id,
                                'name': extra_obj.name,
                                'price': float(extra_obj.price),
                                'quantity': 1  # Or get quantity from the form if needed
                            })
                        except Extra.DoesNotExist:
                            continue
                    item['extras'] = extras
                # Always recalculate subtotal based on current extras
                extras_for_calc = item.get('extras', [])
                item['subtotal'] = item['price'] * quantity + sum(
                    extra.get('price', 0) * quantity for extra in extras_for_calc
                )
                break

        request.session['order'] = order
        return redirect('orderDetails')

    return redirect('orderDetails')


######################### empty order ######################################


def emptyOrder(request):
    print('this is the empty function ')
    # Check if 'order' exists in session and remove it
    if 'order' in request.session:
        request.session.pop('order', None)
        # Optionally mark the session as modified
        request.session.modified = True

    # Option 1: Redirect to another page after clearing
    return JsonResponse({"status": "success", "message": "Cart was emptied successfully."}) # Replace 'home' with your actual URL name
# ###################### submit order ########################################
# @csrf_exempt
# def submitOrder(request):
#     if request.method == "POST":
     
#         # Get the order data from the session
#         order_data = request.session.get('order', [])
     
#         # Ensure there are items in the session
#         if not order_data:
#             return JsonResponse({"status": "error", "message": "No items in the cart."}, status=400)
       
#         # Fetch or create the "Pending" order status
#         pending_status, created = OrderStatus.objects.get_or_create(name='pending')
        
#         table_number = request.session.get('table_number', None)
#         print ('this is the table number ' + str(table_number))
       
#         if table_number:
 
#             orderTable = Table.objects.get(number=table_number)
#             # orderTable = Table.objects.get(number=table_number)
         
#         else:
      
#             orderTable = Table.objects.get(number='Take Away')
            
  
      
        
        
#         if request.user.is_authenticated:
#           try:
#         # Assuming the logged-in user is linked to a Customer object
#             customer = Customer.objects.get(user=request.user)
#             order = Order.objects.create(
#             customer=customer,  # Link the customer to the order
#             order_status=pending_status,
#             total_amount=0,
#             table=orderTable
#           )
#           except Customer.DoesNotExist:
#         # If the user is logged in but not a customer, leave the customer field null
#             order = Order.objects.create(
#             order_status=pending_status,
#             total_amount=0,
#             table=orderTable
#           )

#         else:
#           order = Order.objects.create(
#             order_status=pending_status, 
#             total_amount=0,  
#             table=orderTable
#           )
            
    
     
#         total_amount = 0  # Initialize the total amount for the order
#         orderTable.status = 'occupied'
#         orderTable.save()
#         # Loop through the items from the session and create OrderItems
#         for item_data in order_data:
        
#             item = Item.objects.get(id=item_data['item_id'])  # Fetch the item from the database
           
    
#             # Create the OrderItem
#             order_item = OrderItem.objects.create(
#                 order=order,
#                 item=item,
#                 quantity=item_data['quantity'],
#                 price=item_data['price'] * item_data['quantity'],  # Calculate price based on quantity
#                 customizations=item_data['customizations']
#             )
#             order_item.save()
        
#             # Add the selected extras to the OrderItem
#             # Safeguard: Only process extras if they are dicts with 'id' and 'quantity'
#             extras_list = item_data.get('extras', [])
#             if isinstance(extras_list, list):
#                 for extra_data in extras_list:
#                     if (
#                         isinstance(extra_data, dict)
#                         and 'id' in extra_data
#                         and 'quantity' in extra_data
#                     ):
#                         extra = Extra.objects.get(id=extra_data['id'])
#                         order_item.selected_extras.add(extra, through_defaults={'quantity': extra_data['quantity']})
#                         OrderItemExtra.objects.create(
#                             order_item=order_item,
#                             extra=extra,
#                             quantity=extra_data['quantity']
#                         )
#             order_item.save()
#             # Update the running total amount
#             total_amount += order_item.price

#         # Update the total amount of the order
#         order.total_amount = total_amount
#         order.save(update_fields=["total_amount"])

#         # Clear the session as the order is now confirmed and saved in the database
#         request.session['order'] = []
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#         "admin_notifications",
#         {
#             "type": "order_notification",
#             "order_id": order.id,
#             "customer": order.customer.user.username if order.customer and order.customer.user else "Guest",
#             "total": str(order.total_amount),
#             "timestamp": timezone.now().isoformat()
#         }
#     )

#         # Return a success response
#         return JsonResponse({"status": "success", "message": "Order submitted successfully."})

#     return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)
#######################################submit order waiter edition #############################################
@csrf_exempt
@transaction.atomic # Use a transaction to ensure the whole order saves or none of it does
def submitOrder(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

    order_data = request.session.get('order', [])
    if not order_data:
        return JsonResponse({"status": "error", "message": "Your cart is empty."}, status=400)

    # --- 1. SETUP THE ORDER ENVIRONMENT ---

    # Fetch the "Pending" status for the new order
    try:
        pending_status = OrderStatus.objects.get(name__iexact='pending')
    except OrderStatus.DoesNotExist:
        # This is a critical error, the system isn't set up correctly
        return JsonResponse({"status": "error", "message": "Order status 'pending' not found."}, status=500)

    # Determine the table for the order
    table_number = request.session.get('table_number')
    try:
        orderTable = Table.objects.get(number=table_number) if table_number else Table.objects.get(number='Take Away')
    except Table.DoesNotExist:
        return JsonResponse({"status": "error", "message": f"Table '{table_number or 'Take Away'}' not found."}, status=400)

    # --- 2. CREATE THE MAIN ORDER INSTANCE ---

    # Generate a unique, sequential display ID for the order
    today = date.today()
    counter, _ = DailyOrderCounter.objects.get_or_create(date=today)
    counter.counter += 1
    counter.save()
    display_id = f"{today.strftime('%Y%m%d')}-{counter.counter:03d}"

    # Identify the customer and/or staff member from the request user
    customer = None
    staff_waiter = None
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            pass  # User is not a customer
        try:
            staff_waiter = Staff.objects.get(user=request.user)
        except Staff.DoesNotExist:
            pass  # User is not a staff member

    # Create the main Order object with an initial total of 0
    order = Order.objects.create(
        customer=customer,
        waiter=staff_waiter,
        order_status=pending_status,
        total_amount=0,  # Will be calculated and updated later
        table=orderTable,
        table_number=orderTable.number,
        display_id=display_id
    )

    # Mark the table as occupied
    orderTable.status = 'occupied'
    orderTable.save()

    total_order_amount = 0

    # --- 3. CREATE ORDER ITEMS AND EXTRAS (Corrected Loop) ---

    for item_data in order_data:
        try:
            item = Item.objects.get(id=item_data['item_id'])
            extras_list_data = item_data.get('extras', [])
        except Item.DoesNotExist:
            continue # Skip if an item from the session is no longer in the DB

        # Loop for each quantity of the main item (e.g., for 2 burgers, this loop runs twice)
        for _ in range(item_data['quantity']):
            # Create one OrderItem instance for this single unit
            order_item = OrderItem.objects.create(
                order=order,
                item=item,
                item_name=item.name,
                item_price=item.price,
                price=item.price,  # Set initial price, model's save() will update it
                customizations=item_data.get('customizations', '')
            )

            # Add all its extras to THIS specific OrderItem
            for extra_data in extras_list_data:
                try:
                    extra = Extra.objects.get(id=extra_data['id'])
                    OrderItemExtra.objects.create(
                        order_item=order_item,
                        extra=extra,
                        quantity=1,  # The quantity of an extra is always 1
                        extra_name=extra.name,
                        extra_price=extra.price
                    )
                except Extra.DoesNotExist:
                    continue # Skip if an extra is no longer in the DB

            # Trigger the model's save method to recalculate the price with extras
            order_item.save()
            
            # Add this single item's final, recalculated price to the order's total
            total_order_amount += order_item.price

    # --- 4. FINALIZE THE ORDER ---

    # Update the total amount of the entire order with the calculated sum
    order.total_amount = total_order_amount
    order.save(update_fields=["total_amount"])

    # Clear the cart from the session
    request.session['order'] = []
    request.session.pop('table_number', None) # Also clear the table number

    # --- 5. SEND NOTIFICATIONS AND RESPOND ---

    # Determine redirect URL based on user role
    if staff_waiter and staff_waiter.role.lower() == 'manager':
        redirect_url = reverse('admin_dashboard')
    else:
        redirect_url = reverse('table_landing_page')

    # Send real-time notification via Channels
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
    ####################################### set table number waiters Edition###############################################

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


####################################### print Items view ############################################



def printOrder(request):
    # Fetch the order items from the session
    # orders=Order.objects.filter(order_status='readytoprint')
    order_items = request.session.get('order', [])
 
    
    # If there are no items in the session, display a message
    if not order_items:
        return JsonResponse({"status": "error", "message": "Your order is empty."}, status=400)

    # Prepare the data for rendering
    formatted_order_items = []
    total_amount = 0  # Initialize total amount

    for item in order_items:
        # Fetch extras and their prices for each item
        extras = item.get('extras', [])
        extra_price = sum(extra['price'] for extra in extras)  # Calculate total price of extras

        subtotal =item['subtotal'] # Calculate subtotal for each item
        formatted_order_items.append({
            'item_id':item['item_id'],
            'name': item['name'],
            'quantity': item['quantity'],
            'unit_price': item['price'],
            'extras': extras if extras else 'None',
            # 'extras': ', '.join(extra['name'] for extra in extras) if extras else 'None',
            'extra_price': extra_price,
            'subtotal': subtotal,
            'table':item['table']
             
        })

        # Add to the total amount
        total_amount += subtotal
        total_amount = round(total_amount, 2)

    # Render the page with order items and total amount
    return JsonResponse({
        'order_items': formatted_order_items,
        'total_amount': total_amount
    })


# ################################### login view ####################################

# def login_view(request):
 

#     if request.method == "POST":
     
#         try:
        
#             username= request.POST.get('email') or json.loads(request.body).get('email')
#             password = request.POST.get('password') or json.loads(request.body).get('password')
        
           
                 
#             if not username or not password:
#                 messages.error(request, "Both email and password are required.")
#                 return render(request, 'login.html')

#             user = authenticate(request, username=username, password=password)
            
#             if user is not None:
            
#                 login(request, user)
                
#                 if hasattr(user, 'staff'):
#                     return redirect('admin_dashboard')
#                 else:
#                     return redirect('index')
#             else:
#                 messages.error(request, "Invalid email or password.")
#                 return render(request, 'login.html')
#         except json.JSONDecodeError:
#             messages.error(request, "Invalid request format.")
#             return render(request, 'login.html')
        
#     return render(request, 'login.html')


##################################### login view waiter edition ##########################

def login_view(request):
 

    if request.method == "POST":
     
        try:
        
            username= request.POST.get('email') or json.loads(request.body).get('email')
            password = request.POST.get('password') or json.loads(request.body).get('password')
            username = username.strip()
           
           
                 
            if not username or not password:
                messages.error(request, "Both email and password are required.")
                return render(request, 'login.html')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
            
                login(request, user)
                
                if hasattr(user, 'staff'):
                    staff = Staff.objects.get(user=user)
                    if staff.is_active and not staff.inHold:
                    # Redirect based on staff role
                      if staff.role == 'waiter':
                        return redirect('table_landing_page')
                      else:
                        return redirect('admin_dashboard')
                else:
                    return redirect('index')
            else:
                messages.error(request, "Invalid email or password.")
                return render(request, 'login.html')
        except json.JSONDecodeError:
            messages.error(request, "Invalid request format.")
            return render(request, 'login.html')
        
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
################################################ dashboard view 
@login_required
def adminDashboard(request):
    # Fetch all tables
    tables = Table.objects.all().order_by('id')
    
    # Get filter parameters
    selected_table_id = request.GET.get('table_id')
    status_filter = request.GET.get('status')
    
    # Base queryset
    orders = Order.objects.filter(inHold=False).order_by('-ordered_at')
    
    # Apply table filter if provided
    if selected_table_id:
        orders = orders.filter(table__id=selected_table_id)
    
    # Apply status filter if provided
    if status_filter:
        if status_filter == 'cancelled':
            orders = orders.filter(order_status__name='cancelled')
        elif status_filter == 'non_cancelled':
            orders = orders.exclude(order_status__name='cancelled')
        else:
            orders = orders.filter(order_status__name=status_filter)
    
    # Get status counts for filter display
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

def customer_home(request):
    return render(request, 'customer_home.html') 



############################ customer signup ########################################
@csrf_exempt
def signup(request):

    if request.method == 'POST':
        try:
         
           
            data = json.loads(request.body)
            name = data['name']
            email = data['email']
            phone_number = data['phone_number']
            address = data['address']
            password = data['password']

            # Check if email already exists
            if User.objects.filter(email=email).exists():
             
                return JsonResponse({"status": "error", "message": "Email is already in use."},status=409)

            # Create User

            user = User.objects.create_user(username=name, email=email, password=password)

            # Create Customer linked to the user
            Customer.objects.create(user=user, phone_number=phone_number,address=address)
         

            return JsonResponse({"status": "success", "message": "Sign-Up successful!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)


def customerSignup(request):

  return render(request, 'customer_signup.html')



# ############################################## customer profile view ################################# 
@login_required
def customerProfile(request):
    # Get the logged-in customer (assuming Customer model has OneToOne with User)
    customer = Customer.objects.get(user=request.user)
    
    # Get the customer's order history
    orders = Order.objects.filter(customer=customer)

    if request.method == 'POST':
        # Update the customer profile if the form is submitted
        print('requst is post here ')
        customer.name = request.POST.get('name')
        print (customer.user.username)
        customer.user.username = request.POST.get('name')
        print (customer.user.username)
        customer.phone_number = request.POST.get('phone_number')
        customer.address = request.POST.get('address')
        customer.save()
        customer.user.save()
        print('finished saving')
        messages.success(request, "Profile updated successfully.")

        # Redirect to the same page after updating
        return redirect('customer_profile')
 
    # Pass customer info and order history to the template
    return render(request, 'customer_profile.html', {'customer': customer, 'orders': orders})

############################################## delete orders ########################################
@login_required
def deleteOrder(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = get_object_or_404(Order, id=order_id)
            
            # Update order with deletion details
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
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON data"
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
    
    return JsonResponse({
        "success": False,
        "error": "Invalid request method. Use POST."
    }, status=405)


############################################ update order statues ######################################
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
            
            # Get the order and the new status
            order = get_object_or_404(Order, id=order_id)
            new_status = get_object_or_404(OrderStatus, name=new_status_name)

            # Update the order status
            order.order_status = new_status
            order.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."})
    
############################### cancel order view ###################################################
@login_required
def cancelled_orders(request):
    # Get filter parameters
    table_number = request.GET.get('table_number')
    date = request.GET.get('date')
    
    # Start with base queryset
    cancelled_orders = Order.objects.filter(inHold=True).select_related(
        'customer', 'deleted_by', 'table'
    ).order_by('-deleted_at')
    
    # Apply filters if provided
    if table_number:
        cancelled_orders = cancelled_orders.filter(table__number=table_number)
    
    if date:
        print('this is the dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee '+date)
        cancelled_orders = cancelled_orders.filter(deleted_at__date=date)
    
    # Get all tables for the filter dropdown
    tables = Table.objects.all().values_list('number', flat=True).distinct()
    
    # Get unique dates for the date filter
    order_dates = Order.objects.filter(inHold=True).exclude(
        deleted_at__isnull=True
    ).dates('deleted_at', 'day').distinct()
    
    # Prepare context for template rendering
    context = {
        'cancelled_orders': cancelled_orders,
        'tables': tables,
        'order_dates': order_dates,
        'selected_table': table_number,
        'selected_date': date,
        'page_title': 'Cancelled Orders'
    }
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        data = [{
            'id': order.id,
            'table_number': order.table_number,
            'total_amount': str(order.total_amount),
            'deleted_by': order.deleted_by.get_full_name() if order.deleted_by else 'System',
            'deleted_reason': order.deleted_reason,
            'deleted_at': order.deleted_at.isoformat() if order.deleted_at else None,
            'ordered_at': order.ordered_at.isoformat(),
            'deleted_by': order.deleted_by.get_full_name() if order.deleted_by else 'System',
        } for order in cancelled_orders]
        return JsonResponse(data, safe=False)
    
    # Return HTML for regular requests
    return render(request, 'deleted_orders.html', context)
    
    ################################### print order view ######################################

def print_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    csrf_token = get_token(request)

    if request.method == "POST":
        try:
            printed_status = OrderStatus.objects.get(name="printed")
            order.order_status = printed_status
            order.printed_at = timezone.now()
            order.save()
            return JsonResponse({"success": True, "message": "Print confirmed."})
        except OrderStatus.DoesNotExist:
            return JsonResponse({"success": False, "message": "Printed status not found."}, status=500)

    # Grouping logic
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

    
@login_required
def cancelled_orders(request):
    # Get filter parameters
    table_number = request.GET.get('table_number')
    date = request.GET.get('date')
    
    # Start with base queryset
    cancelled_orders = Order.objects.filter(inHold=True).select_related(
        'customer', 'deleted_by', 'table'
    ).order_by('-deleted_at')
    
    # Apply filters if provided
    if table_number:
        cancelled_orders = cancelled_orders.filter(table__number=table_number)
    
    if date:
        cancelled_orders = cancelled_orders.filter(deleted_at__date=date)
    
    # Get all tables for the filter dropdown
    tables = Table.objects.all().values_list('number', flat=True).distinct()
    
    # Get unique dates for the date filter
    order_dates = Order.objects.filter(inHold=True).exclude(
        deleted_at__isnull=True
    ).dates('deleted_at', 'day').distinct()
    
    context = {
        'cancelled_orders': cancelled_orders,
        'tables': tables,
        'order_dates': order_dates,
        'selected_table': table_number,
        'selected_date': date,
        'page_title': 'Cancelled Orders'
    }
    
    # Return JSON if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{
            'id': order.id,
            'customer_name': order.customer.name if order.customer else 'Walk-in',
            'table_number': order.table_number,
            'total_amount': str(order.total_amount),
            'deleted_by': order.deleted_by.get_full_name() if order.deleted_by else 'System',
            'deleted_reason': order.deleted_reason,
            'deleted_at': order.deleted_at.isoformat() if order.deleted_at else None,
            'ordered_at': order.ordered_at.isoformat()
        } for order in cancelled_orders]
        return JsonResponse(data, safe=False)
    
    # Return HTML for regular requests
    return render(request, 'deleted_orders.html', context)



# @login_required
# def generate_invoice(request, table_id):
#   if request.method == "POST":
#     try:

#       today = date.today()
#       counter, _ = DailyOrderCounter.objects.get_or_create(date=today)
#       counter.counter += 1
#       counter.save()
#       display_id = f"{today.strftime('%Y%m%d')}-{counter.counter:03d}"
#       table = get_object_or_404(Table, id=table_id)
  
#       data = json.loads(request.body)
 

#       orders_id = data.get('order_select', [])  # Get the selected orders from the JSON data
#       completed_status = OrderStatus.objects.filter(name='completed').first()
#       if not completed_status:
#         return JsonResponse({
#         "success": False,
#          "message": "Completed status not found."
#         }, status=500)
#       if orders_id:
#                 # Filter the selected orders
#         orders = Order.objects.filter(id__in=orders_id, order_status__name__in=['served', 'printed'], inHold=False)
#         if not orders.exists():
#           return JsonResponse({"success": False, "message": "No served orders for this table."}, status=404)

#       else:
#         orders = Order.objects.filter(table=table, order_status__name__in=['served', 'printed'], inHold=False)

#         if not orders.exists():
#           return JsonResponse({"success": False, "message": "No served or printed  orders for this table."}, status=404)

#       total_amount = sum(order.total_amount for order in orders)
#       invoice = Invoice.objects.create(
#         table=table, 
#         total_amount=total_amount, 
#         created_at=timezone.now(),
#         display_id=display_id
#       )
      
      
   

# # Update orders with the completed status
#       orders.update(invoice=invoice, order_status=completed_status)
#       table.status = 'available'
#       table.save()
   
#       return JsonResponse({"success": True, "message": "Invoice generated successfully."})
#     except Exception as e:
#       return JsonResponse({"success": False, "message": str(e)}, status=500)
#   else: 
#     return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

@login_required
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


@login_required
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

@login_required
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

@login_required
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
@login_required
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


@csrf_exempt
@login_required
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
@login_required
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


@login_required
def sales_report(request):
    # Get today's date properly
    today = timezone.now().date()
    start_date = today.replace(day=1)  # Start of current month
    end_date = today

    # Process date parameters from GET request
    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass  # Keep default if invalid format
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass  # Keep default if invalid format

    # Convert dates to datetime objects for proper filtering
    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    # Filter invoices within the date range
    invoices = Invoice.objects.filter(
        created_at__range=[start_datetime, end_datetime]
    ).exclude(inHold=True)

    # Calculate sales summary from invoices
    total_sales = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)
    num_orders = invoices.count()
    avg_order_value = invoices.aggregate(avg_value=Avg('total_amount'))['avg_value'] or Decimal(0)

    # Get item sales data
    item_sales = (
        OrderItem.objects.filter(
            invoice__in=invoices
        ).values('item__name')
        .annotate(
            total_items_sold=Count('id'),
            total_revenue=Sum('price')
        ).order_by('-total_items_sold')
    )

    # --- Corrected Logic: Payment Breakdown ---
    # Filter payments within the selected date range
    payments_in_range = Payment.objects.filter(
        created_at__range=[start_datetime, end_datetime], # <-- THE FIX IS HERE
        inHold=False
    )

    # Aggregate payment totals by method from the correctly filtered payments
    payment_method_summary = (
        payments_in_range.values('method')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    # Prepare data for the pie chart
    payment_labels = [p['method'] for p in payment_method_summary]
    payment_data = [float(p['total']) for p in payment_method_summary]

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'num_orders': num_orders,
        'avg_order_value': avg_order_value,
        'item_sales': item_sales,
        'payment_method_summary': payment_method_summary,
        'payment_labels': payment_labels,
        'payment_data': payment_data,
    }

    return render(request, 'sales_report.html', context)





@login_required
def payment_report(request):
    """
    Provides a detailed report of invoices with payment methods broken down
    into columns, including a grand total summary row.
    """
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today

    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError: pass
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError: pass

    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    # --- Core Logic ---

    # Base queryset of invoices that have payments in the selected date range
    invoices_with_payments = Invoice.objects.filter(
        payments__created_at__range=[start_datetime, end_datetime]
    ).distinct()

    # Subqueries for each payment method (Card removed)
    cash_subquery = Payment.objects.filter(invoice=OuterRef('pk'), method='CASH').values('invoice').annotate(total=Sum('amount')).values('total')
    bank_subquery = Payment.objects.filter(invoice=OuterRef('pk'), method='CARD').values('invoice').annotate(total=Sum('amount')).values('total')
    momo_subquery = Payment.objects.filter(invoice=OuterRef('pk'), method='MOMO').values('invoice').annotate(total=Sum('amount')).values('total')

    # Annotate the main invoice query with the calculated values
    invoices_report = invoices_with_payments.annotate(
        cash_total=Coalesce(Subquery(cash_subquery), Value(0), output_field=DecimalField()),
        bank_total=Coalesce(Subquery(bank_subquery), Value(0), output_field=DecimalField()),
        momo_total=Coalesce(Subquery(momo_subquery), Value(0), output_field=DecimalField()),
    ).annotate(
        total_paid=F('cash_total') + F('bank_total') + F('momo_total')
    ).order_by('-created_at')

    # --- NEW: Calculate Grand Totals ---
    # Perform the aggregation on the entire filtered queryset before pagination
    grand_totals = invoices_report.aggregate(
        total_billed=Sum('total_amount'),
        total_paid=Sum('total_paid'),
        total_cash=Sum('cash_total'),
        total_bank=Sum('bank_total'),
        total_momo=Sum('momo_total'),
    )

    # Apply pagination to the detailed list
    paginator = Paginator(invoices_report, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'grand_totals': grand_totals, # Pass the totals to the template
        'start_date_str': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date_str': end_date.strftime('%Y-%m-%d') if end_date else '',
    }

    return render(request, 'payment_report.html', context)

############################# waiter report ##############################################
@login_required
def staff_report(request):
    # Default date range to the current month
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today

    # Process date parameters from GET request, same as in sales_report
    if request.method == "GET":
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

    # Convert dates to datetime objects for filtering
    start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
    end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))

    # --- Core Logic for Staff Performance ---

    # 1. Get all active staff members and their user details
    # We use select_related('user') for an efficient database query
    staff_members = Staff.objects.filter(is_active=True).select_related('user')

    # 2. Annotate each staff member with the count of orders they served in the date range
    # We use a Subquery to perform this calculation efficiently
    orders_served_query = Order.objects.filter(
        waiter=OuterRef('pk'),
        ordered_at__range=[start_datetime, end_datetime]
    ).values('waiter').annotate(count=Count('pk')).values('count')

    # 3. Annotate each staff member with the total amount from invoices they created
    # Note: This assumes the 'created_by' field on the Invoice model links to a User
    # We need to link from Staff -> User -> Invoice
    invoices_total_query = Invoice.objects.filter(
        # This assumes your Invoice model has a `created_by` ForeignKey to User
        created_by=OuterRef('user_id'), 
        created_at__range=[start_datetime, end_datetime]
    ).values('created_by').annotate(total=Sum('total_amount')).values('total')

    # 4. Combine the queries
    staff_performance_data = staff_members.annotate(
        orders_served_count=Subquery(orders_served_query),
        invoices_created_total=Subquery(invoices_total_query)
    ).order_by('-invoices_created_total') # Order by most valuable staff first

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'staff_performance_data': staff_performance_data,
    }

    return render(request, 'staff_report.html', context)

@login_required
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
############################# table landing page waiter edition ###################################
def tableLanding(request):
    tables = Table.objects.filter(inHold=False).order_by('section', 'number')
    tables_json = serializers.serialize('json', tables)
    print('this is the tables count'+str(tables.count))
    return render(request, 'tables_landing_page.html', {'tables_json': tables_json})

 ################################change table ########################################################   
@login_required
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

@login_required
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

@login_required
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

@login_required
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
############################## grt order by table waiter edition ########################
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



# def getOrderByTable(request, tableId):
#     table = get_object_or_404(Table, id=tableId)

#     # Fetch all orders for this table
#     orders = Order.objects.filter(table=table).order_by('-created_at').prefetch_related('orderitem_set__selected_extras')

#     # Prepare data for the template
#     all_orders_data = []
#     for order in orders:
#         order_items = order.orderitem_set.all()
#         all_orders_data.append({
#             'order': order,
#             'order_items': order_items,
#         })

#     context = {
#         'table': table,
#         'all_orders_data': all_orders_data,
#     }

#     return render(request, 'order_view.html', context)


######################### move order to another table #########################
@login_required

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
        