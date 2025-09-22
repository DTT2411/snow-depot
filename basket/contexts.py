from decimal import Decimal
from django.conf import settings

from products.models import Product


def basket_contents(request):
    """
    Build basket items and totals from the session for global template access
    """
    basket_items = []
    total = Decimal('0.00')
    item_count = 0

    basket = request.session.get('basket', {})

    for item_id, quantity in basket.items():
        try:
            product = Product.objects.get(pk=item_id)
        except Product.DoesNotExist:
            # Skip invalid product ids that might linger in the session
            continue
        line_total = product.price * quantity
        total += line_total
        item_count += quantity
        basket_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
            'line_total': line_total,
        })

    delivery = (total * Decimal(settings.DELIVERY_PERCENTAGE) / Decimal('100')) if total > 0 else Decimal('0.00')
    grand_total = total + delivery

    context = {
        'basket_items': basket_items,
        'total': total,
        'item_count': item_count,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return context
