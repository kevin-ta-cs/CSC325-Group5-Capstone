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
    ownership_question = forms.CharField(
        required=False,
        max_length=255,
        help_text="Claimants answer privately. Avoid revealing the answer in the description.",
    )

    image = forms.ImageField(
        required=False,
        help_text="New images stay private until an admin approves them.",
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = FoundItem
        fields = (
            'report_type',
            'item_name',
            'description',
            'category',
            'location',
            'specific_area',
            'ownership_question',
            'date_found',
            'time_found',
            'image',
        )
        widgets = {
            'report_type': forms.HiddenInput(),
            'date_found': forms.DateInput(attrs={'type': 'date'}),
            'time_found': forms.TimeInput(attrs={'type': 'time'}),
            'specific_area': forms.TextInput(
                attrs={'placeholder': 'Floor, room, or nearby landmark'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get('report_type') == 'found'
            and not cleaned_data.get('time_found')
        ):
            self.add_error('time_found', 'Enter the time the item was found.')
        if cleaned_data.get('report_type') == 'lost':
            cleaned_data['ownership_question'] = ''
            cleaned_data['time_found'] = None
        return cleaned_data

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