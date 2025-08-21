from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json
from .models import Customer, Staff
from orders.models import Order

def login_view(request):
    if request.method == "POST":
        try:
            username = request.POST.get('email') or json.loads(request.body).get('email')
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
                        if staff.role == 'waiter':
                            return redirect('reservations:table_landing_page')
                        else:
                            return redirect('orders:admin_dashboard')
                else:
                    return redirect('core:index')
            else:
                messages.error(request, "Invalid email or password.")
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
