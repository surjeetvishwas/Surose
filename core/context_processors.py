from .models import ProductCart

def cart(request):
    if request.user.is_authenticated:
        carts = ProductCart.objects.filter(user=request.user, order=None)
    else:
        carts = []
    return {'global_carts': {
        'count': len(carts),
    }}