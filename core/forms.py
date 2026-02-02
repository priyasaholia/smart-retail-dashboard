from django import forms
from .models import NotebookEntry


class NotebookEntryForm(forms.ModelForm):
    class Meta:
        model = NotebookEntry
        fields = ["entry_type", "amount", "description"]

        widgets = {
            "entry_type": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe the transaction or note clearly"
                }
            ),
        }


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserSignupForm(UserCreationForm):
    ACCOUNT_CHOICES = [
        ("customer", "Customer"),
        ("retailer", "Retailer"),
    ]

    email = forms.EmailField(required=True)
    account_type = forms.ChoiceField(choices=ACCOUNT_CHOICES, initial="customer", widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "account_type")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # keep account inactive until verification
        user.is_active = False
        if commit:
            user.save()
            # ensure profile exists and store account_type
            try:
                profile = user.profile
            except Exception:
                from .models import Profile
                profile = Profile.objects.create(user=user)
            profile.account_type = self.cleaned_data.get("account_type", "customer")
            profile.save()
        return user
