from django.contrib import admin

from .models import FoundItem


@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "reporter", "category", "location", "date_found")
    list_filter = ("category", "location")
    search_fields = ("item_name", "description")
