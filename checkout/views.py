from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from basket.contexts import basket_contents

import stripe


def checkout(request):
    basket = request.session.get('basket', {})
    if not basket:
        messages.error(request, "Your basket is empty!")
        return redirect(reverse('products'))

    order_form = OrderForm()
    totals = basket_contents(request)
    grand_total = totals['grand_total']
    stripe_total = round(grand_total * 100)
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51S02vFRxaGtB2eQBXQGgUUBZHU652gy2URNDUCXHBsgV3HvkgyvYgs2jVSW0h3rP88vF14cFdPsKvp5PfYKbE5Mm00TRdfSzcX',
        # 'grand_total': grand_total,
        # 'stripe_total': stripe_total,
        'client_secret': 'test client secret',
    }

    return render(request, template, context)
