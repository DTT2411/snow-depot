from django.shortcuts import render


# Create your views here.
def view_basket(request):
    """
    A view to show the current shopping basket page
    """
    return render(request, 'basket/basket.html')
