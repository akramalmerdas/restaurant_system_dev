from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

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