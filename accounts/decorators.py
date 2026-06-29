from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    """
    Decorator to restrict view access based on our custom user roles.
    Example: @role_required(allowed_roles=['admin'])
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Treat superusers as admin inherently
            if request.user.is_superuser and 'admin' in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            if getattr(request.user, 'role', None) in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied # This triggers an HTTP 403 Forbidden error
        return _wrapped_view
    return decorator