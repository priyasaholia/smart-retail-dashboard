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
