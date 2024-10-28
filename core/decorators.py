from django.shortcuts import redirect



def only_anonymous(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def only_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def only_in(roles):
    def inner(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.role in roles:
                if 'admin' in roles and request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
                return redirect('core:home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return inner