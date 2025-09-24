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

    # Optional variant attributes from form
    size = request.POST.get('product_size')
    boot_size = request.POST.get('product_boot_size')
    ski_length = request.POST.get('product_ski_length')
    pole_length = request.POST.get('product_pole_length')

    if size:
        item_record = basket.get(pid, {})
        items_by_size = item_record.get('items_by_size', {})
        items_by_size[size] = items_by_size.get(size, 0) + quantity
        item_record['items_by_size'] = items_by_size
        basket[pid] = item_record
        messages.success(request, f'Added {quantity} × "{product.name}" (size {size}) to your basket.')
    elif boot_size:
        item_record = basket.get(pid, {})
        items_by_boot_size = item_record.get('items_by_boot_size', {})
        items_by_boot_size[boot_size] = items_by_boot_size.get(boot_size, 0) + quantity
        item_record['items_by_boot_size'] = items_by_boot_size
        basket[pid] = item_record
        messages.success(request, f'Added {quantity} × "{product.name}" (boot size {boot_size}) to your basket.')
    elif ski_length:
        item_record = basket.get(pid, {})
        items_by_ski_length = item_record.get('items_by_ski_length', {})
        items_by_ski_length[ski_length] = items_by_ski_length.get(ski_length, 0) + quantity
        item_record['items_by_ski_length'] = items_by_ski_length
        basket[pid] = item_record
        messages.success(request, f'Added {quantity} × "{product.name}" (ski length {ski_length}) to your basket.')
    elif pole_length:
        item_record = basket.get(pid, {})
        items_by_pole_length = item_record.get('items_by_pole_length', {})
        items_by_pole_length[pole_length] = items_by_pole_length.get(pole_length, 0) + quantity
        item_record['items_by_pole_length'] = items_by_pole_length
        basket[pid] = item_record
        messages.success(request, f'Added {quantity} × "{product.name}" (pole length {pole_length}) to your basket.')
    else:
        basket[pid] = basket.get(pid, 0) + quantity
        messages.success(request, f'Added {quantity} × "{product.name}" to your basket.')

    request.session['basket'] = basket

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
