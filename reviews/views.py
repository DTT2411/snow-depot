from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.views.decorators.http import require_POST

from products.models import Product
from .forms import ReviewForm
from .models import Review


@require_POST
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, 'Review submitted successfully!')
    else:
        # Persist form errors via Django messages if needed
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    return redirect(reverse('product_detail', args=[product.id]))


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    product_id = review.product_id
    if request.user.is_superuser or review.user_id == request.user.id:
        review.delete()
        messages.success(request, 'Review deleted.')
    else:
        messages.error(request, 'You do not have permission to delete this review.')
    return redirect(reverse('product_detail', args=[product_id]))


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    # Only the author can edit; admins can delete but not edit
    if review.user_id != request.user.id:
        messages.error(request, 'You do not have permission to edit this review.')
        return redirect(reverse('product_detail', args=[review.product_id]))

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect(reverse('product_detail', args=[review.product_id]))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review,
        'product': review.product,
    })
