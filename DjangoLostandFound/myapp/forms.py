from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import FoundItem, FoundItemInquiry


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')


class DashboardUsernameForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username',)


class FoundItemForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        help_text="New images stay private until an admin approves them.",
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = FoundItem
        fields = (
            'item_name',
            'description',
            'category',
            'location',
            'date_found',
            'time_found',
            'image',
        )
        widgets = {
            'date_found': forms.DateInput(attrs={'type': 'date'}),
            'time_found': forms.TimeInput(attrs={'type': 'time'}),
        }

    def save(self, commit=True):
        found_item = super().save(commit=False)
        if self.files.get(self.add_prefix("image")):
            found_item.image_approved = False
        if commit:
            found_item.save()
            self.save_m2m()
        return found_item


class FoundItemInquiryForm(forms.ModelForm):
    class Meta:
        model = FoundItemInquiry
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'maxlength': 1000}),
        }