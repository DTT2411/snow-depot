from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages

from products.models import Product


# Create your views here.
def view_basket(request):
    """
    A view to show the current shopping basket page
    """
    return render(request, 'basket/basket.html')


def add_to_basket(request, product_id):
    """
    Add a quantity of the specified product to the basket (session-based)
    Expects POST with 'quantity' and optional 'redirect_url'
    """
    if request.method != 'POST':
        return redirect('view_basket')

    product = get_object_or_404(Product, pk=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        messages.error(request, 'Quantity must be at least 1.')
        redirect_url = request.POST.get('redirect_url') or reverse('view_basket')
        return redirect(redirect_url)

    basket = request.session.get('basket', {})
    pid = str(product_id)
    basket[pid] = basket.get(pid, 0) + quantity

    request.session['basket'] = basket
    messages.success(request, f'Added {quantity} × "{product.name}" to your basket.')

    redirect_url = request.POST.get('redirect_url') or reverse('view_basket')
    return redirect(redirect_url)


def adjust_basket(request, product_id):
    """
    Adjust the quantity of the specified product to the given amount.
    If quantity <= 0, the item is removed.
    """
    if request.method != 'POST':
        return redirect('view_basket')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    basket = request.session.get('basket', {})
    pid = str(product_id)

    if quantity > 0:
        basket[pid] = quantity
        messages.success(request, 'Basket updated.')
    else:
        if pid in basket:
            basket.pop(pid)
        messages.success(request, 'Item removed from basket.')

    request.session['basket'] = basket
    return redirect('view_basket')


def remove_from_basket(request, product_id):
    """
    Remove the specified product from the basket entirely
    """
    basket = request.session.get('basket', {})
    pid = str(product_id)

    if pid in basket:
        basket.pop(pid)
        request.session['basket'] = basket
        messages.success(request, 'Item removed from basket.')
    return redirect('view_basket')
