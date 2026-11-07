from django import forms
from django.utils import timezone

from .models import LostItem


class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = (
            "item_name",
            "description",
            "category",
            "location_lost",
            "date_lost",
        )
        widgets = {
            "item_name": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 4}),
            "category": forms.TextInput(),
            "location_lost": forms.TextInput(),
            "date_lost": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        for field_name in ("item_name", "description", "category", "location_lost"):
            value = cleaned_data.get(field_name)
            if value is not None:
                value = value.strip()
                if value:
                    cleaned_data[field_name] = value
                else:
                    self.add_error(field_name, "This field cannot be blank.")

        date_lost = cleaned_data.get("date_lost")
        if date_lost and date_lost > timezone.localdate():
            self.add_error("date_lost", "The lost date cannot be in the future.")

        return cleaned_data
