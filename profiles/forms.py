from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(required=False)
    class Meta:
        model = UserProfile
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_town_or_city': 'Town or City',
            'default_county': 'County or State',
            'default_postcode': 'Postal Code',
        }

        if 'full_name' in self.fields:
            self.fields['full_name'].widget.attrs['autofocus'] = True
            if hasattr(self.instance, 'user') and self.instance.user:
                self.fields['full_name'].initial = self.instance.user.get_full_name()
        ordered_fields = ['full_name'] + [f for f in self.fields if f != 'full_name']
        self.order_fields(ordered_fields)
        for field in self.fields:
            if field != 'default_country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = ('border-black rounded-0 profile-form-input')
            self.fields[field].label = False
