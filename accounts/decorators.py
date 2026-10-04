from functools import wraps
from django.http import HttpResponseForbidden


def role_required(*roles):
    """
    Decorator that checks if the user is authenticated and belongs to one of the allowed roles.
    Superusers are automatically granted Admin access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You must be logged in.")
            
            user_role = getattr(request.user, 'role', None)
            is_superuser = getattr(request.user, 'is_superuser', False)

            if user_role not in roles and not (is_superuser and 'Admin' in roles):
                return HttpResponseForbidden("You do not have permission to access this page.")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

