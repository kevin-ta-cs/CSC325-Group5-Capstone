from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html

from .models import FoundItem


class FoundItemAdminForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = FoundItem
        fields = "__all__"


@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    form = FoundItemAdminForm
    list_display = (
        "item_name",
        "reporter",
        "category",
        "location",
        "date_found",
        "image_approved",
    )
    list_filter = ("category", "location", "image_approved")
    readonly_fields = ("image_preview",)
    search_fields = ("item_name", "description")

    @admin.display(description="Uploaded image")
    def image_preview(self, obj):
        if not obj or not obj.image:
            return "No image uploaded."
        return format_html(
            '<a href="{}">View uploaded image</a>',
            reverse("found_item_image", args=(obj.pk,)),
        )

    def save_model(self, request, obj, form, change):
        if "image" in form.changed_data:
            obj.image_approved = False
        super().save_model(request, obj, form, change)
