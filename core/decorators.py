from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def staff_member_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff member.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return redirect('login')

        if not hasattr(request.user, 'staff'):
            messages.error(request, "You are not authorized to access this page.")
            return redirect('index') # Or a custom 'unauthorized' page

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator for views that checks that the user is a staff member with an 'admin' or 'manager' role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return redirect('login')

        if not hasattr(request.user, 'staff'):
            messages.error(request, "You are not authorized to access this page.")
            return redirect('index')

        staff = request.user.staff
        if staff.role.lower() not in ['admin', 'manager']:
            messages.error(request, "You do not have the required permissions to access this page.")
            return redirect('admin_dashboard') # Redirect to a safe page for staff

        return view_func(request, *args, **kwargs)
    return _wrapped_view

from django.contrib.auth.mixins import AccessMixin

class StaffRequiredMixin(AccessMixin):
    """
    Mixin for class-based views that checks that the user is logged in and is a staff member.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return self.handle_no_permission()
        if not hasattr(request.user, 'staff'):
            messages.error(request, "You are not authorized to access this page.")
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
