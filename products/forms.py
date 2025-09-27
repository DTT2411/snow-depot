from django import forms
from .models import Product, Category, Subcategory


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        subcategories = Subcategory.objects.all()
        category_friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        subcategory_friendly_names = [(sc.id, sc.get_friendly_name()) for sc in subcategories]

        self.fields['category'].choices = category_friendly_names
        self.fields['subcategory'].choices = subcategory_friendly_names