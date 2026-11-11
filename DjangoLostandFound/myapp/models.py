from django.conf import settings
from django.db import models


ITEM_CATEGORY_CHOICES = (
    ("Accessories", "Accessories"),
    ("Bags & Luggage", "Bags & Luggage"),
    ("Electronics", "Electronics"),
    ("Keys", "Keys"),
)

BUILDING_CHOICES = (
    ("Amphitheater", "Amphitheater"),
    ("Aviation Center", "Aviation Center"),
    ("Broad Hollow Bioscience Park One", "Broad Hollow Bioscience Park One"),
    ("Broad Hollow Bioscience Park Two", "Broad Hollow Bioscience Park Two"),
    ("Campus Center", "Campus Center"),
    ("Campus Commons", "Campus Commons"),
    ("Conference Center", "Conference Center"),
    ("Gleeson Hall", "Gleeson Hall"),
    ("Greenley Library", "Greenley Library"),
    ("Hale Hall", "Hale Hall"),
    ("Hooper Hall", "Hooper Hall"),
    ("Horton Hall", "Horton Hall"),
    ("Knapp Hall", "Knapp Hall"),
    ("Laffin Hall", "Laffin Hall"),
    ("Lupton Hall", "Lupton Hall"),
    ("Memorial Hall", "Memorial Hall"),
    ("Nold Athletic Complex", "Nold Athletic Complex"),
    ("Quintyne Hall", "Quintyne Hall"),
    ("Roosevelt Hall", "Roosevelt Hall"),
    ("School of Business", "School of Business"),
    ("Sinclair Hall", "Sinclair Hall"),
    ("Thompson Hall", "Thompson Hall"),
    ("Ward Hall", "Ward Hall"),
    ("Whitman Hall", "Whitman Hall"),
)


class FoundItem(models.Model):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="found_items",
    )
    item_name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=32, choices=ITEM_CATEGORY_CHOICES)
    location = models.CharField(max_length=160, choices=BUILDING_CHOICES)
    date_found = models.DateField()
    time_found = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name
