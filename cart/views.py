from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from shop.models import Product


@login_required
def cart_add(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if cart_item.quantity <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.info(request, 'Item added to cart')
        else:
            messages.warning(request, 'Not enough stock')
    except CartItem.DoesNotExist:
        if product.stock > 0:
            CartItem.objects.create(product=product, quantity=1, cart=cart)
            messages.info(request, 'Item added to cart')
        else:
            messages.warning(request, 'Not enough stock')

    return redirect('cart:cart_detail')


@login_required
def cart_remove(request, id):
    cart = Cart.objects.get(user=request.user)
    product = get_object_or_404(Product, id=id, available=True)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    cart_item.delete()
    messages.info(request, 'Cart item removed.')

    return redirect('cart:cart_detail')


@login_required
def cart_clear(request):
    cart = Cart.objects.get(user=request.user)
    cart.delete()
    messages.info(request, 'Cart cleared.')
    return redirect('cart:cart_detail')


@login_required
def cart_update(request, id):
    if request.method == 'POST':
        cart = Cart.objects.get(user=request.user)
        product = Product.objects.get(id=id, available=True)
        cart_item = CartItem.objects.get(product=product, cart=cart)
        quantity = int(request.POST['quantity'])

        if quantity < product.stock:
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
                messages.info(request, 'Cart item removed.')
        else:
            messages.warning(request, 'Not enough stock.')

    return redirect('cart:cart_detail')


@login_required
def item_increment(request, id):
    cart = Cart.objects.get(user=request.user)
    product = Product.objects.get(id=id, available=True)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity <= cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.warning(request, 'Not enough stock.')

    return redirect('cart:cart_detail')


@login_required
def item_decrement(request, id):
    cart = Cart.objects.get(user=request.user)
    product = Product.objects.get(id=id, available=True)
    cart_item = CartItem.objects.get(product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
        messages.info(request, f'Cart item removed.')

    return redirect('cart:cart_detail')


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
        
    return render(request, 'cart/cart_detail.html', {'cart': cart, 'cart_items': cart_items})