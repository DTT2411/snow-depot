from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from products.models import Product
from basket.contexts import basket_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    Caches checkout session data to Stripe PaymentIntent metadata for future
    retrieval; stores basket, save_info, and username. Returns 200 or error
    response.
    """
    try:
        client_secret = request.POST.get('client_secret', '')
        if not client_secret:
            return HttpResponse(status=400)
        pid = client_secret.split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'basket': json.dumps(request.session.get('basket', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request, 'Payment cannot be processed. Please try again later.'
            )
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Display and process the checkout: validate order form, create Order and
    line items, initialize Stripe PaymentIntent, handle payment submission,
    and render checkout page with client secret and form.
    """

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        basket = request.session.get('basket', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'town_or_city': request.POST['town_or_city'],
            'county': request.POST['county'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            if request.user.is_authenticated:
                # Links order to the user's profile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                order.user_profile = profile
            client_secret = request.POST.get('client_secret', '')
            if not client_secret:
                messages.error(
                    request,
                    'Missing payment confirmation. Please try again.',
                )
                return redirect(reverse('checkout'))
            pid = client_secret.split('_secret')[0]
            order.stripe_pid = pid
            order.original_basket = json.dumps(basket)
            order.save()
            for item_id, item_data in basket.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        if item_data.get('items_by_size'):
                            for size, quantity in item_data[
                                'items_by_size'
                            ].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
                        elif item_data.get('items_by_boot_size'):
                            for boot_size, quantity in item_data[
                                'items_by_boot_size'
                            ].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_boot_size=boot_size,
                                )
                                order_line_item.save()
                        elif item_data.get('items_by_ski_length'):
                            for ski_length, quantity in item_data[
                                'items_by_ski_length'
                            ].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_ski_length=ski_length,
                                )
                                order_line_item.save()
                        elif item_data.get('items_by_pole_length'):
                            for pole_length, quantity in item_data[
                                'items_by_pole_length'
                            ].items():
                                order_line_item = OrderLineItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_pole_length=pole_length,
                                )
                                order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        (
                            'One of the products in your basket was not found '
                            'in our database.'
                        ),
                    )
                    order.delete()
                    return redirect(reverse('view_basket'))

            request.session['save_info'] = 'save-info' in request.POST
            return redirect(
                reverse('checkout_success', args=[order.order_number])
                )
        else:
            messages.error(
                request,
                (
                    'There was an error in your form. '
                    'Please double check your information.'
                ),
            )
            context = {
                'order_form': order_form,
                'stripe_public_key': stripe_public_key,
                'client_secret': request.POST.get('client_secret', ''),
            }
            return render(request, 'checkout/checkout.html', context)

    else:
        basket = request.session.get('basket', {})
        if not basket:
            messages.error(request, "Your basket is empty!")
            return redirect(reverse('products'))

        totals = basket_contents(request)
        grand_total = totals['grand_total']
        stripe_total = round(grand_total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        if not stripe_public_key:
            messages.warning(
                request,
                'Stripe public key missing - needs to be set in environment.',
            )

        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        return render(request, template, context)


def checkout_success(request, order_number):
    """
    Finalizes a successful checkout. Attaches order to user profile,
    optionally updates saved profile info, clears basket, displays
    confirmation message, and renders the order confirmation page.
    """
    save_info = request.session.get('save_info')  # Update later
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        #  Attaches the user profile to the order
        order.user_profile = profile
        order.save()

        if save_info:
            # Updates the full name tied to the user account
            full_name = (order.full_name or '').strip()
            if full_name:
                parts = full_name.split()
                request.user.first_name = parts[0]
                request.user.last_name = (
                    ' '.join(parts[1:]) if len(parts) > 1 else ''
                )
                request.user.save()

            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(
        request,
        (
            f'Order complete! Your order number is {order_number}. '
            f'You will receive a confirmation email at {order.email}.'
        ),
    )

    if 'basket' in request.session:
        del request.session['basket']

    template = 'checkout/checkout_success.html'

    context = {
        'order': order,
    }

    return render(request, template, context)
