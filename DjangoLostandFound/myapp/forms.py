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
    class Meta:
        model = FoundItem
        fields = (
            'item_name',
            'description',
            'category',
            'location',
            'date_found',
            'time_found',
        )
        widgets = {
            'date_found': forms.DateInput(attrs={'type': 'date'}),
            'time_found': forms.TimeInput(attrs={'type': 'time'}),
        }


class FoundItemInquiryForm(forms.ModelForm):
    class Meta:
        model = FoundItemInquiry
        fields = ('message',)
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'maxlength': 1000}),
        }