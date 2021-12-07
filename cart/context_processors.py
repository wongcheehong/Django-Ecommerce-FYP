from .models import Cart, CartItem


def counter(request):

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        item_count = cart_items.count

        return dict(item_count=item_count)
    else:
        return {}


