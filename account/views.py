import json
import urllib
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegisterForm, UserEditForm, ProfileEditForm, AddressForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Address
from django.http import JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.conf import settings
from .models import User

def register(request):
    key = settings.RECAPTCHA_SITE_KEY
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())

            if not result['success']:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                return render(request, 'registration/register.html', {'form': form, 'key': key})
            else:
                email = form.cleaned_data['email']
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already in use. If you forgot password, try forgot password.')
                    return render(request, 'registration/register.html', {'form': form, 'key': key})
                new_user = form.save()
                Profile.objects.create(user=new_user)
                messages.success(request, 'Your account have been created. Try login now.')
                return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form, 'key': key})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/user_edit.html', {'user_form': user_form, 'profile_form': profile_form})





def address_create(request):
    if request.method == 'POST':
        address_form = AddressForm(data=request.POST)
        address_list = Address.objects.filter(user=request.user)

        if(address_list.count()<5):
            if address_form.is_valid():
                name = address_form.cleaned_data['address_name']
                address = address_form.cleaned_data['address']
                state = address_form.cleaned_data['address_state']
                city = address_form.cleaned_data['address_city']
                zip = address_form.cleaned_data['address_zip']

                new_address = Address.objects.create(
                    user=request.user,
                    address_name=name,
                    street_address=address,
                    state=state,
                    city=city,
                    zip=zip
                )

                default_shipping = Address.objects.filter(default_shipping=True, user=request.user)
                default_billing = Address.objects.filter(default_billing=True, user=request.user)
                if not default_shipping.exists():
                    new_address.default_shipping = True
                    new_address.save()
                if not default_billing.exists():
                    new_address.default_billing = True
                    new_address.save()

                messages.success(request, 'A new address has been created.')
                return JsonResponse({'status': 'ok'})
            else:
                messages.warning(request, 'Your form data is invalid')
                return JsonResponse({'status': 'bad request'})
        else:
            messages.info(request, 'You can only store up to 5 addresses. Delete and try again.')
            return JsonResponse({'status': 'bad request'})
    else:
        form = AddressForm()
        return render(request, "address/address_creation_form.html", {'form': form})


def address_book(request):
    if request.method == 'GET':
        try:
            default_shipping_address = Address.objects.get(default_shipping=True, user=request.user)
            default_billing_address = Address.objects.get(default_billing=True, user=request.user)
            shipping_address = Address.objects.filter(default_shipping=False, user=request.user)
            billing_address = Address.objects.filter(default_billing=False, user=request.user)
            address_form = AddressForm()
            context = {
                'default_shipping_address': default_shipping_address,
                'default_billing_address': default_billing_address,
                'shipping_address': shipping_address,
                'billing_address': billing_address,
                'form': address_form,
            }
        except ObjectDoesNotExist:
            form = AddressForm()
            context = {
                'form': form
            }
    return render(request, 'address/address_book.html', context)


def change_shipping_default(request):
    if request.method == 'POST':
        default_shipping = Address.objects.get(default_shipping=True, user=request.user)
        shipping_id = request.POST.get('select_shipping')
        change_shipping = Address.objects.get(id=shipping_id, user=request.user)

        default_shipping.default_shipping = False
        default_shipping.save()
        change_shipping.default_shipping = True
        change_shipping.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def change_billing_default(request):
    if request.method == 'POST':
        default_billing = Address.objects.get(default_billing=True, user=request.user)
        billing_id = request.POST.get('select_billing')
        change_billing = Address.objects.get(id=billing_id, user=request.user)

        default_billing.default_billing = False
        default_billing.save()
        change_billing.default_billing = True
        change_billing.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def update_address(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        address = get_object_or_404(Address, id=id, user=request.user)

        data = serializers.serialize("json", [address])

        return JsonResponse(data, safe=False)
    else:
        id = request.POST.get('id')
        print(id)
        address_name = request.POST.get('address_name')
        address = request.POST.get('address')
        address_state = request.POST.get('address_state')
        address_city = request.POST.get('address_city')
        address_zip = request.POST.get('address_zip')

        address_obj = get_object_or_404(Address, id=id, user=request.user)
        address_obj.address_name = address_name
        address_obj.street_address = address
        address_obj.state = address_state
        address_obj.city = address_city
        address_obj.zip = address_zip
        address_obj.save()

        return JsonResponse({'status': 'ok'})


def delete_address(request):
    id = request.POST.get('id')
    address = Address.objects.get(id=id, user=request.user)

    if address.default_billing or address.default_shipping:
        messages.warning(request, 'You cannot delete default address')
        return JsonResponse({'status': 'bad request'})
    else:
        address.delete()
        messages.success(request, 'You address is successfully deleted')

    print(id)

    return JsonResponse({'status': 'ok'})


