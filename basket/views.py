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
    Add a product to the session basket.

    Accepts POST with quantity and optionally one sizing attribute
    (product_size, product_boot_size, product_ski_length, product_pole_length).
    Increments either a non-sized quantity or the matching items_by_* entry,
    persists the basket in the session, shows a message, and redirects to the
    basket (or a provided redirect_url).
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

    # Optional size/length attributes from product detail form
    size = request.POST.get('product_size')
    boot_size = request.POST.get('product_boot_size')
    ski_length = request.POST.get('product_ski_length')
    pole_length = request.POST.get('product_pole_length')

    # Handle first provided sizing (priority: size -> boot_size -> ski_length -> pole_length)
    sizings = [
        (size, 'items_by_size', 'size'),
        (boot_size, 'items_by_boot_size', 'boot size'),
        (ski_length, 'items_by_ski_length', 'ski length'),
        (pole_length, 'items_by_pole_length', 'pole length'),
    ]

    for size_value, map_key, label in sizings:
        if size_value:
            item_record = basket.get(pid, {})
            mapping = item_record.get(map_key, {})
            mapping[size_value] = mapping.get(size_value, 0) + quantity
            item_record[map_key] = mapping
            basket[pid] = item_record
            messages.success(request, f'Added {quantity} × "{product.name}" ({label} {size_value}) to your basket.')
            break
    else:
        basket[pid] = basket.get(pid, 0) + quantity
        messages.success(request, f'Added {quantity} × "{product.name}" to your basket.')

    request.session['basket'] = basket

    redirect_url = request.POST.get('redirect_url') or reverse('view_basket')
    return redirect(redirect_url)


def adjust_basket(request, product_id):
    """
    Adjust the quantity of the specified product or its specific sizing to the given amount.
    - If a sizing (size/boot_size/ski_length/pole_length) is provided, update that mapping.
    - If no sizing is provided and the product is non-sized, update the plain quantity.
    - If quantity <= 0, remove the item of that specific sizing.
    """
    if request.method != 'POST':
        return redirect('view_basket')

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    basket = request.session.get('basket', {})
    pid = str(product_id)

    if pid not in basket:
        return redirect('view_basket')

    # Sizing attributes from form
    size = request.POST.get('product_size')
    boot_size = request.POST.get('product_boot_size')
    ski_length = request.POST.get('product_ski_length')
    pole_length = request.POST.get('product_pole_length')

    item_data = basket.get(pid)

    def update_sizing(map_key: str, size_value: str):
        nonlocal item_data
        if not isinstance(item_data, dict):
            item_data = {}
        mapping = item_data.get(map_key, {})
        if quantity > 0:
            mapping[size_value] = quantity
            messages.success(request, 'Basket updated.')
        else:
            if size_value in mapping:
                mapping.pop(size_value)
            messages.success(request, 'Item removed from basket.')
        if mapping:
            item_data[map_key] = mapping
            basket[pid] = item_data
        else:
            # Remove this mapping; if no other mappings remain, remove the product entry
            if map_key in item_data:
                item_data.pop(map_key, None)
            if any(k.startswith('items_by_') for k in item_data.keys()):
                basket[pid] = item_data
            else:
                basket.pop(pid, None)

    if size:
        update_sizing('items_by_size', size)
    elif boot_size:
        update_sizing('items_by_boot_size', boot_size)
    elif ski_length:
        update_sizing('items_by_ski_length', ski_length)
    elif pole_length:
        update_sizing('items_by_pole_length', pole_length)
    else:
        # No sizing provided
        if isinstance(item_data, int):
            if quantity > 0:
                basket[pid] = quantity
                messages.success(request, 'Basket updated.')
            else:
                basket.pop(pid, None)
                messages.success(request, 'Item removed from basket.')
        elif isinstance(item_data, dict):
            # Try to update unambiguously if only one sizing and one key exist
            for mk in ('items_by_size', 'items_by_boot_size', 'items_by_ski_length', 'items_by_pole_length'):
                if mk in item_data:
                    keys = list(item_data[mk].keys())
                    if len(keys) == 1:
                        update_sizing(mk, keys[0])
                        break
            else:
                # Ambiguous: cannot determine which sizing to update
                messages.warning(request, 'Please resubmit specifying the sizing to update.')

    request.session['basket'] = basket
    return redirect('view_basket')


def remove_from_basket(request, product_id):
    """
    Remove the specified product or a specific sizing from the basket.
    - If a sizing is provided (size/boot_size/ski_length/pole_length), remove only that entry.
    - If no sizing is provided and the item is non-sized, remove the whole product.
    - If no sizing is provided but multiple sizing exist, do not remove all; warn the user.
    """
    basket = request.session.get('basket', {})
    pid = str(product_id)

    size = request.POST.get('product_size')
    boot_size = request.POST.get('product_boot_size')
    ski_length = request.POST.get('product_ski_length')
    pole_length = request.POST.get('product_pole_length')

    if pid in basket:
        item_data = basket.get(pid)

        def remove_sizing(map_key: str, size_value: str):
            nonlocal item_data
            if not isinstance(item_data, dict):
                return False
            mapping = item_data.get(map_key, {})
            if size_value not in mapping:
                return False
            mapping.pop(size_value)
            if mapping:
                item_data[map_key] = mapping
                basket[pid] = item_data
            else:
                item_data.pop(map_key, None)
                # If no other sizing mappings remain, remove the whole product
                if any(k.startswith('items_by_') and item_data.get(k) for k in item_data.keys()):
                    basket[pid] = item_data
                else:
                    basket.pop(pid, None)
            return True

        removed = False
        if size:
            removed = remove_sizing('items_by_size', size)
        elif boot_size:
            removed = remove_sizing('items_by_boot_size', boot_size)
        elif ski_length:
            removed = remove_sizing('items_by_ski_length', ski_length)
        elif pole_length:
            removed = remove_sizing('items_by_pole_length', pole_length)
        else:
            # No sizing provided
            if isinstance(item_data, int):
                basket.pop(pid)
                removed = True
            elif isinstance(item_data, dict):
                # If unambiguous (only one sizing key with a single entry), remove that one
                for mk in ('items_by_size', 'items_by_boot_size', 'items_by_ski_length', 'items_by_pole_length'):
                    if mk in item_data and isinstance(item_data[mk], dict) and len(item_data[mk]) == 1:
                        only_key = next(iter(item_data[mk]))
                        removed = remove_sizing(mk, only_key)
                        break
                if not removed:
                    messages.warning(request, 'Please try removing again; specify the size/length to remove.')

        if removed:
            request.session['basket'] = basket
            messages.success(request, 'Item removed from basket.')

    return redirect('view_basket')
