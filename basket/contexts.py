from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def basket_contents(request):
    """
    Build and return the basket context used across templates.
    - Reads the session-based basket and normalizes its contents into a
      list of basket_items that templates can iterate over. Supports both
      sized and non-sized products.
    - Calculates running totals (subtotal, delivery, grand total) and the
      overall item_count.
    - Returns a context dict with basket_items and totals for rendering in
      the header, basket and checkout pages.
    """
    basket_items = []
    total = Decimal('0.00')
    item_count = 0

    basket = request.session.get('basket', {})

    for item_id, item_data in basket.items():
        if isinstance(item_data, int):
            try:
                product = Product.objects.get(pk=item_id)
            except Product.DoesNotExist:
                # Skip invalid product ids that might linger in the session after admin change/deletion
                continue
            line_total = product.price * item_data
            total += line_total
            item_count += item_data
            # Creates a dictionary of current session basket items
            basket_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
                'line_total': line_total,
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            if item_data.get('items_by_size'):
                for size, quantity in item_data['items_by_size'].items():
                    line_total = product.price * quantity
                    total += line_total
                    item_count += quantity
                    basket_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'product': product,
                        'size': size,
                        'line_total': line_total,
                    })
            elif item_data.get('items_by_boot_size'):
                for boot_size, quantity in item_data['items_by_boot_size'].items():
                    line_total = product.price * quantity
                    total += line_total
                    item_count += quantity
                    basket_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'product': product,
                        'boot_size': boot_size,
                        'line_total': line_total,
                    })
            elif item_data.get('items_by_ski_length'):
                for ski_length, quantity in item_data['items_by_ski_length'].items():
                    line_total = product.price * quantity
                    total += line_total
                    item_count += quantity
                    basket_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'product': product,
                        'ski_length': ski_length,
                        'line_total': line_total,
                    })
            elif item_data.get('items_by_pole_length'):
                for pole_length, quantity in item_data['items_by_pole_length'].items():
                    line_total = product.price * quantity
                    total += line_total
                    item_count += quantity
                    basket_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'product': product,
                        'pole_length': pole_length,
                        'line_total': line_total,
                    })

    # Decimal quantize method is used to round up the delivery & grand total to 2 decimal places
    delivery = ((total * Decimal(settings.DELIVERY_PERCENTAGE) / Decimal('100')) if total > 0 else Decimal('0.00')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grand_total = (total + delivery).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    context = {
        'basket_items': basket_items,
        'total': total,
        'item_count': item_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
