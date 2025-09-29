from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Subcategory


class ProductForm(forms.ModelForm):
    """
    ModelForm for creating and editing products; configures category &
    subcategory choices, image upload widget, rating constraints, and
    applies consistent styling classes to all fields.
    """

    class Meta:
        model = Product
        exclude = ('image_url',)
        widgets = {
            'rating': forms.NumberInput(
                attrs={'min': 0, 'max': 5, 'step': 0.1}
                ),
            'price': forms.NumberInput(
                attrs={'min': 0, 'max': 9999.9, 'step': 1}
                ),
        }

    image = forms.ImageField(
        label='Image', required=False, widget=CustomClearableFileInput
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        category_friendly_names = [
            (c.id, c.get_friendly_name()) for c in categories
        ]
        subcategory_friendly_names = [
            (sc.id, sc.get_friendly_name()) for sc in subcategories
        ]

        self.fields['category'].choices = category_friendly_names
        self.fields['subcategory'].choices = subcategory_friendly_names

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
