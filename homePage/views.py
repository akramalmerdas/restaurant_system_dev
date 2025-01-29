from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from item.models import Item ,Order,OrderItem,Extra,OrderItemExtra,OrderStatus,Customer,Table,Invoice
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required
 
# Create your views here.
from django.shortcuts import render, get_object_or_404


def index(request):
    # Fetch table_id from the query parameter
    table_number = request.GET.get('table_id')
    # table = None

    # If table_id is provided, fetch the table object
    if table_number:
        try:
          
            request.session['table_number'] = table_number
            print('here we print the table number'+table_number)
        except Table.DoesNotExist:
            table_number = None  # Handle invalid table_id gracefully

    # Fetch menu items as usual
    lunchItems = Item.objects.filter(category__id=2)
    saladItems = Item.objects.filter(category__id=1)
    hotDrinksItems = Item.objects.filter(category__id=9)
    coldDrinksItems = Item.objects.filter(category__id=10)
    breakFast = Item.objects.filter(category__id=12)
    extras = Item.objects.filter(category__id=11)
    crepes = Item.objects.filter(category__id=8)
    smoothies = Item.objects.filter(category__id=7)
    burgers = Item.objects.filter(category__id=6)
    pizzas = Item.objects.filter(category__id=5)
    soups = Item.objects.filter(category__id=4)
    sandwiches = Item.objects.filter(category__id=3)
    user = request.user

    # Pass the table object to the template
    return render(request, 'index.html', {
        'lunch': lunchItems,
        'salad': saladItems,
        'hot': hotDrinksItems,
        'cold': coldDrinksItems,
        'breakFast': breakFast,
        'extra': extras,
        'crepe': crepes,
        'smoothie': smoothies,
        'burger': burgers,
        'pizza': pizzas,
        'soup': soups,
        'sandwich': sandwiches,
        'user': user
      #  'table': table,  # Include the table in the context
    })




# def get_extras(request):
#   extras = Extra.objects.all().values('name', 'price')
#   return JsonResponse(list(extras), safe=False)


def orderPage(request, menu_item_id):  
    item = get_object_or_404(Item, id=menu_item_id)
    # extras = ExtraItem.objects.filter(item__id=menu_item_id).select_related('Extra').values('Extra__name', 'Extra__price') 
    # extras_list = [{'name': extra['Extra__name'], 'price': float(extra['Extra__price'])} for extra in extras]
   
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
            'extras': ', '.join(extra['name'] for extra in extras) if extras else 'None',
            'extra_price': extra_price,
            'subtotal': subtotal,
            'table':item['table']
             
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
            'total_amount': total_amount
        }
    )







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

        # Create a new order item structure
        order_item = {
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
        if item['item_id'] == item_id:  # Match the item by its ID
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


# ###################### submit order ########################################

   

@csrf_exempt
def submitOrder(request):
    if request.method == "POST":
        # Get the order data from the session
        order_data = request.session.get('order', [])
        
        # Ensure there are items in the session
        if not order_data:
            return JsonResponse({"status": "error", "message": "No items in the cart."}, status=400)
        
        # Fetch or create the "Pending" order status
        pending_status, created = OrderStatus.objects.get_or_create(name='readytoprint')
 
        table_number=request.session.get('table_number', None)
        orderTable = Table.objects.get(number=table_number)
      
        
        if request.user.is_authenticated:
          try:
        # Assuming the logged-in user is linked to a Customer object
            customer = Customer.objects.get(user=request.user)
            order = Order.objects.create(
            customer=customer,  # Link the customer to the order
            order_status=pending_status,
            total_amount=0,
            table=orderTable
          )
          except Customer.DoesNotExist:
        # If the user is logged in but not a customer, leave the customer field null
            order = Order.objects.create(
            order_status=pending_status,
            total_amount=0,
            table=orderTable
          )

        else:
          order = Order.objects.create(
            order_status=pending_status, 
            total_amount=0,  
            table=orderTable
          )
            
    
      
     
        total_amount = 0  # Initialize the total amount for the order

        # Loop through the items from the session and create OrderItems
        for item_data in order_data:
        
            item = Item.objects.get(id=item_data['item_id'])  # Fetch the item from the database
           
    
            # Create the OrderItem
            order_item = OrderItem.objects.create(
                order=order,
                item=item,
                quantity=item_data['quantity'],
                price=item_data['price'] * item_data['quantity'],  # Calculate price based on quantity
                customizations=item_data['customizations']
            )
            order_item.save()
        
            # Add the selected extras to the OrderItem
            for extra_data in item_data['extras']:
                extra = Extra.objects.get(id=extra_data['id'])  # Fetch extra from the database
                order_item.selected_extras.add(extra, through_defaults={'quantity': extra_data['quantity']})
                
                # Create a corresponding OrderItemExtra instance
                OrderItemExtra.objects.create(
                    order_item=order_item,
                    extra=extra,
                    quantity=extra_data['quantity']  # Use the quantity from the session data
                )
            order_item.save()
            # Update the running total amount
            total_amount += order_item.price

        # Update the total amount of the order
        order.total_amount = total_amount
        order.save(update_fields=["total_amount"])

        # Clear the session as the order is now confirmed and saved in the database
        request.session['order'] = []

        # Return a success response
        return JsonResponse({"status": "success", "message": "Order submitted successfully."})

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)



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
            'extras': ', '.join(extra['name'] for extra in extras) if extras else 'None',
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

def login_view(request):
 

    if request.method == "POST":
     
        try:
        
            username= request.POST.get('email') or json.loads(request.body).get('email')
            password = request.POST.get('password') or json.loads(request.body).get('password')
        
           
                 
            if not username or not password:
                messages.error(request, "Both email and password are required.")
                return render(request, 'login.html')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
            
                login(request, user)
                
                if hasattr(user, 'staff'):
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

def adminDashboard(request):
       # Fetch all tables
    tables = Table.objects.all()

    # Get the selected table ID from the request
    selected_table_id = request.GET.get('table_id')

    # Filter orders by the selected table, if provided
    if selected_table_id:
        orders = Order.objects.filter(table__id=selected_table_id)
    else:
        orders = Order.objects.all()
    return render(request, 'admin_dashboard.html',{   
         'tables': tables,
        'orders': orders,
        'selected_table_id': selected_table_id,})     

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
def deleteOrder(request, order_id):
    if request.method == 'POST':  # Ensure it's a POST request
        # Get the order object or return a 404 error if not found
        order = get_object_or_404(Order, id=order_id)
        
        # Set the inHold field to True
        order.inHold = True
        order.save()
        
        # Return a success response
        return JsonResponse({"message": "Order marked as in hold successfully!"})

    # Return an error response for invalid methods
    return JsonResponse({"error": "Invalid request method."}, status=405)


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
    


    ################################### print order view ######################################

def print_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    csrf_token = get_token(request)

    if request.method == "POST":
        # Handle the confirmation of the print
        try:
            printed_status = OrderStatus.objects.get(name="printed")
            order.order_status = printed_status
            order.printed_at = timezone.now() 
            order.save()
            print('Print confirmed successfully')
            return JsonResponse({"success": True, "message": "Print confirmed."})
        except Order.DoesNotExist:
            print('order not found ')
            return JsonResponse({"success": False, "message": "Order not found."}, status=404)
        except OrderStatus.DoesNotExist:
            print('an error happened')
            return JsonResponse({"success": False, "message": "Printed status not found."}, status=500)

    # Render the print page if it's a GET request
    return render(request, 'print_order.html', {
        'order': order,
        'order_id': order_id,
        'csrf_token': csrf_token
    })

# @csrf_exempt
# def confirm_print(request, order_id):
#     if request.method == "POST":
#         try:
#             order = Order.objects.get(id=order_id)
#             printed_status = OrderStatus.objects.get(name="printed")
#             order.order_status = printed_status
#             order.save()
#             print('confirmed successfully')
#             return JsonResponse({"success": True, "message": "Print confirmed."})
#         except Order.DoesNotExist:  
#             return JsonResponse({"success": False, "message": "Order not found."}, status=404)
#         except OrderStatus.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Printed status not found."}, status=500)
#     return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)



def generate_invoice(request, table_id):
    # Get the table
    table = get_object_or_404(Table, id=table_id)

    # Fetch all completed orders for the table
    orders = Order.objects.filter(table=table, order_status__name='served', invoice__isnull=True)

    if not orders.exists():
        return JsonResponse({"success": False, "message": "No completed orders for this table."}, status=404)

    # Calculate the total amount
    total_amount = sum(order.total_amount for order in orders)

    # Create an invoice with the current time
    invoice = Invoice.objects.create(
        table=table, 
        total_amount=total_amount, 
        created_at=timezone.now()  # Use timezone.now() for proper time zone handling
    )

    # Associate the orders with the invoice
    orders.update(invoice=invoice)

    # If you're rendering the invoice page, you can pass the invoice and orders to the template
    return render(request, 'invoice.html', {'invoice': invoice, 'orders': orders})




def invoice_dashboard(request):
    table_id = request.GET.get('table_id')  # Get the table ID from the query parameters
    tables = Table.objects.all()  # Fetch all tables for the filter dropdown

    if table_id:
        invoices = Invoice.objects.filter(table_id=table_id)
    else:
        invoices = Invoice.objects.all()

    return render(request, 'invoice_dashboard.html', {
        'invoices': invoices,
        'tables': tables,
        'selected_table_id': table_id,
    })  




def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    orders = Order.objects.filter(invoice__id=invoice_id)# Assuming an Invoice has related Orders
    return render(request, 'invoice.html', {'invoice': invoice, 'orders': orders})
from django.http import JsonResponse

def change_invoice_status(request, invoice_id):
    if request.method == "POST":
        invoice = get_object_or_404(Invoice, id=invoice_id)
        data = json.loads(request.body)  # Parse JSON data
        is_paid = data.get("is_paid")
        if is_paid in ["0", "1"]:
            invoice.is_paid = bool(int(is_paid))
            invoice.save()
            return JsonResponse({"success": True, "message": "Status updated successfully"})
        return JsonResponse({"success": False, "message": "Invalid status value"}, status=400)
    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
