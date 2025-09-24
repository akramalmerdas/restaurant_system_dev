from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
import json
from .models import Customer, Staff
from orders.models import Order

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    print('Login view reached')
    if request.method == "POST":
        try:
            username = request.POST.get('username') or json.loads(request.body).get('username')
            password = request.POST.get('password') or json.loads(request.body).get('password')
            username = username.strip()
            if not username or not password:
                messages.error(request, "Both username and password are required.")
                return render(request, 'login.html')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'staff'):
                    staff = Staff.objects.get(user=user)
                    if staff.is_active and not staff.inHold:
                        if staff.role == 'waiter':
                            return redirect('reservations:table_landing_page')
                        else:
                            return redirect('orders:admin_dashboard')
                else:
                    return redirect('core:index')
            else:
                messages.error(request, "Invalid username or password.")
                return render(request, 'login.html')
        except json.JSONDecodeError:
            messages.error(request, "Invalid request format.")
            return render(request, 'login.html')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data['name']
            email = data['email']
            phone_number = data['phone_number']
            address = data['address']
            password = data['password']
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email is already in use."}, status=409)
            user = User.objects.create_user(username=name, email=email, password=password)
            Customer.objects.create(user=user, phone_number=phone_number, address=address)
            return JsonResponse({"status": "success", "message": "Sign-Up successful!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

def customerSignup(request):
  return render(request, 'customer_signup.html')

@login_required
def customerProfile(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(customer=customer)
    if request.method == 'POST':
        customer.user.username = request.POST.get('name')
        customer.phone_number = request.POST.get('phone_number')
        customer.address = request.POST.get('address')
        customer.save()
        customer.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('users:customer_profile')
    return render(request, 'customer_profile.html', {'customer': customer, 'orders': orders})

@login_required
def get_customers_api(request):
    customers = Customer.objects.filter(inHold=False).order_by('user__username')
    customer_list = [
        {'id': c.id, 'full_name': c.user.get_full_name() or c.user.username}
        for c in customers
    ]
    return JsonResponse(customer_list, safe=False)

@login_required
def customer_dashboard(request):
    customers = Customer.objects.filter(inHold=False).select_related('user').order_by('user__username')
    return render(request, 'customer_dashboard.html', {'customers': customers})

from .forms import CustomerForm

@login_required
def manage_customer(request, customer_id=None):
    if customer_id:
        customer = get_object_or_404(Customer, id=customer_id)
        instance = customer
    else:
        instance = None

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=instance)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']

            if instance: # Editing existing customer
                user = instance.user
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = email or f"{first_name}_{last_name}"
                user.save()
            else: # Creating new customer
                username = email or f"{first_name}_{last_name}_{User.objects.count()}" # simple way to avoid username collision
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )

            customer = form.save(commit=False)
            customer.user = user
            customer.save()

            messages.success(request, f"Customer '{user.get_full_name()}' saved successfully.")
            return redirect('users:customer_dashboard')
    else:
        form = CustomerForm(instance=instance)

    context = {
        'form': form,
        'customer': instance
    }
    return render(request, 'customer_form.html', context)

@login_required
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        user = customer.user
        user.is_active = False
        user.save()

        customer.inHold = True
        customer.save()

        messages.success(request, f"Customer '{user.get_full_name()}' has been deactivated.")
        return redirect('users:customer_dashboard')

    return render(request, 'customer_confirm_delete.html', {'customer': customer})
