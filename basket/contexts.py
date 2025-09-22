from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

from products.models import Product


def basket_contents(request):
    """
    Gets the basket items and totals from the session for global access
    """
    basket_items = []
    total = Decimal('0.00')
    item_count = 0

    basket = request.session.get('basket', {})

    for item_id, quantity in basket.items():
        try:
            product = Product.objects.get(pk=item_id)
        except Product.DoesNotExist:
            # Skip invalid product ids that might linger in the session after admin change/deletion
            continue
        line_total = product.price * quantity
        total += line_total
        item_count += quantity
        # Creates a dictionary of current session basket items
        basket_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
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
