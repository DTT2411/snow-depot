from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Model form for product reviews. Captures text content and optional
    anonymity, validates input length, and adds fields to the Review model for
    create/update.
    """
    content = forms.CharField(
        label="Your review",
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'maxlength': 2000,
                'class': 'form-control rounded-0 border-black',
                'placeholder': 'Share your thoughts about this product...'
            }
        ),
        max_length=2000,
        help_text="Max 2000 characters."
    )
    is_anonymous = forms.BooleanField(
        label="Post as Anonymous",
        required=False,
    )

    class Meta:
        model = Review
        fields = ['content', 'is_anonymous']

    def clean_content(self):
        content = self.cleaned_data.get('content', '')
        content = content.strip()
        if not content:
            raise forms.ValidationError("Review cannot be empty.")
        return content
