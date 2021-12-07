from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core import serializers
from .models import Order, OrderItem
from account.models import Address
from cart.models import CartItem, Cart
from account.forms import AddressForm
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.mail import send_mail
import stripe
import weasyprint

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    is_deleted = False
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.warning(request, 'Not enough stock. Deleted from your cart.')
            item.delete()
            is_deleted = True
        if not item.product.available:
            messages.warning(request, 'Not available. Deleted from your cart.')
            item.delete()
            is_deleted = True

    if is_deleted:
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        shipping_id = request.POST.get('shipping_id')
        billing_id = request.POST.get('billing_id')
        # payment_option = request.POST.get('payment_option')

        shipping_address = get_object_or_404(Address, id=shipping_id, user=request.user)
        billing_address = get_object_or_404(Address, id=billing_id, user=request.user)

        shipping_address_string = f"{shipping_address.street_address}, {shipping_address.zip} " \
                                  f"{shipping_address.city}, {shipping_address.state}"
        billing_address_string = f"{billing_address.street_address}, {billing_address.zip} " \
                                 f"{billing_address.city}, {billing_address.state}"

        order = Order.objects.create(
            user=request.user,
            shipping_name=shipping_address.address_name,
            shipping_address=shipping_address_string,
            billing_name=billing_address.address_name,
            billing_address=billing_address_string,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        order.amount = order.get_total_cost()
        order.save()
        cart.delete()
        # redirect to payment
        # if payment_option == 'card':
        return redirect(to='orders:payment', order_id=order.id)
        # if payment_option == 'fpx':
        #     pass
    else:
        if cart_items.count() == 0:
            return redirect('/shop/')

        try:
            default_shipping_address = Address.objects.get(default_shipping=True, user=request.user)
            default_billing_address = Address.objects.get(default_billing=True, user=request.user)
            shipping_address = Address.objects.filter(default_shipping=False, user=request.user)
            billing_address = Address.objects.filter(default_billing=False, user=request.user)
            context = {
                'cart': cart,
                'cart_items': cart_items,
                'default_shipping_address': default_shipping_address,
                'default_billing_address': default_billing_address,
                'shipping_address': shipping_address,
                'billing_address': billing_address
            }
        except ObjectDoesNotExist:
            form = AddressForm()
            context = {
                'cart': cart,
                'cart_items': cart_items,
                'form': form
            }

    return render(request, 'orders/order/checkout.html', context)


@login_required
@require_GET
def get_address_list(request):
    address_type = request.GET.get('addressType')
    if address_type == 'S':
        addresses = Address.objects.filter(user=request.user).exclude(default_shipping=True)
    else:
        addresses = Address.objects.filter(user=request.user).exclude(default_billing=True)
    data = serializers.serialize("json", addresses)
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def get_address(request):
    address_id = request.GET.get('id')
    address = get_object_or_404(Address, id=address_id, user=request.user)

    data = serializers.serialize("json", [address])
    return JsonResponse(data, safe=False)


@login_required
@require_GET
def my_orders(request):
    type_id = request.GET.get('type')

    if type_id is not None:
        type_id = int(type_id)

    if type_id is None:
        all_orders = Order.objects.filter(user=request.user)
        return render(request, 'orders/order/orders_history.html', {'all_orders': all_orders})
    elif type_id == 1:
        all_orders = Order.objects.filter(user=request.user)
        return render(request, 'orders/order/all_order_list.html', {'all_orders': all_orders})
    elif type_id == 2:
        pending_orders = Order.objects.filter(user=request.user, paid=False, cancelled=False)
        return render(request, 'orders/order/pending_order_list.html', {'pending_orders': pending_orders})
    elif type_id == 3:
        to_ship_orders = Order.objects.filter(user=request.user, paid=True, being_delivered=False)
        return render(request, 'orders/order/to_ship_order_list.html', {'to_ship_orders': to_ship_orders})
    elif type_id == 4:
        to_receive_orders = Order.objects.filter(user=request.user, paid=True, being_delivered=True, received=False)
        return render(request, 'orders/order/to_receive_order_list.html', {'to_receive_orders': to_receive_orders})
    elif type_id == 5:
        completed_orders = Order.objects.filter(user=request.user, paid=True, being_delivered=True, received=True)
        return render(request, 'orders/order/completed_order_list.html', {'completed_orders': completed_orders})
    else:
        cancelled_orders = Order.objects.filter(user=request.user, cancelled=True)
        return render(request, 'orders/order/cancelled_orders_list.html', {'cancelled_orders': cancelled_orders})


@login_required
@require_POST
def receive_order(request):
    order_id = request.POST.get('id')
    order = get_object_or_404(Order, id=order_id, paid=True, received=False, user=request.user)
    order.received = True
    order.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def cancel_order(request):
    order_id = request.POST.get('id')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.paid:
        order.cancelled = True
        order.save()
    else:
        return JsonResponse({'status': 'fail'})

    return JsonResponse({'status': 'ok'})


@login_required
def buy_again(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order, product__available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    for item in order_items:
        product = item.product
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity < product.stock:
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
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, paid=False, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    if request.method == 'GET':
        context = {
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'order': order,
            'order_items': order_items
        }
        return render(request, 'payment/payment.html', context)
    else:
        try:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.username,
                source=request.POST['stripeToken']
            )

            charge = stripe.Charge.create(
                customer=customer,
                amount=int(order.amount * 100),
                currency='myr',
                description=f'Order ID: {order.id}'
            )
            order.paid = True
            order.payment_time = timezone.now()
            order.save()
            send_mail(
                f'Order {order.id}',
                f'You have successfully placed a RM{order.amount} order. Thank you for your purchase!',
                settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=True,
            )
            return render(request, 'payment/payment_done.html', {'order': order})
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.warning(request, f"{err.get('message')}")
            return redirect(f"/orders/payment/{order.id}")
        except stripe.error.RateLimitError as e:
            messages.warning(request, "Rate limit error")
            return redirect(f"/orders/payment/{order.id}")
        except stripe.error.InvalidRequestError as e:
            print(e)
            messages.warning(request, "Invalid parameters")
            return redirect(f"/orders/payment/{order.id}")
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(request, "Not authenticated")
            return redirect(f"/orders/payment/{order.id}")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(request, "Network error")
            return redirect(f"/orders/payment/{order.id}")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(request, "Something went wrong. You were not charged. Please try again.")
            return redirect(f"/orders/payment/{order.id}")
        except Exception as e:
            messages.warning(request, f"A serious error occurred. We have been notified.")
            print(e)
            return redirect("/")


def invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    html = render_to_string('orders/order/invoice.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                                                                  stylesheets=[weasyprint.CSS(
                                                                                      settings.STATIC_URL + 'css/invoice.css')])
    return response
