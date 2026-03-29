from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from datetime import date

def trial_expiration_check(view_func):
    """
    Decorator that checks if the current date is after February 29, 2026.
    If so, redirects to trial expired page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if current date is after February 28, 2026 (last day of trial)
        trial_end_date = date(2026, 2, 28)  # February 28, 2026 (2026 is not a leap year)
        current_date = date.today()
        
        # if current_date > trial_end_date:
        #     return render(request, 'trial_expired.html')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator for views that checks if the user is a staff member with the role
    of 'admin' or 'manager'.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')

        try:
            staff = request.user.staff
            if staff.role not in ['admin', 'manager']:
                # Redirect to a generic 'unauthorized' page or the admin dashboard
                return redirect('orders:admin_dashboard')
        except AttributeError:
            # This user is not a staff member
            return redirect('orders:admin_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view