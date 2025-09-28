from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order


@login_required
def profile(request):
    """
    Displays and updates the authenticated user’s profile, including default
    contact and delivery details, and lists recent orders associated with
    the user.
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Collect's user's full name from form and sets on auth user model
            full_name = form.cleaned_data.get('full_name', '').strip()
            if full_name:
                parts = full_name.split()
                request.user.first_name = parts[0]
                request.user.last_name = (
                    ' '.join(parts[1:]) if len(parts) > 1 else ''
                )
                request.user.save()

            form.save()
            messages.success(
                request,
                'Default delivery information successfully updated!',
            )
            return redirect('profile')
        else:
            messages.error(request, 'Update failed. Please check valid info has been provided in all fields.')
    else:
        form = UserProfileForm(instance=profile)

    orders = profile.orders.all().order_by('-date', '-id')
    template = 'profiles/profile.html'

    context = {
        'form': form,
        'orders': orders,
    }

    return render(request, template, context)


@login_required
def order_history(request, order_number):
    """
    Shows a previous order’s confirmation details when accessed from the user’s
    profile.
    """
    order = get_object_or_404(Order, order_number=order_number)
    messages.info(
        request,
        (
            'This is the old order confirmation for order number '
            f'{order_number}.'
        ),
    )
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)
