from django import forms
from .models import SignUp


class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUp
        fields = ['full_name', 'email']
        # exclude = []

    # Full name validation
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')

        print(full_name)

        if not " " in full_name:
            raise forms.ValidationError("No space in your full name")

        return full_name
