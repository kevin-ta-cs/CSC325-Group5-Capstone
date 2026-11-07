from django.db import models
from django.conf import settings


class LostItem(models.Model):
	item_name = models.CharField(max_length=255)
	description = models.TextField()
	category = models.CharField(max_length=100)
	location_lost = models.CharField(max_length=255)
	date_lost = models.DateField()
	date_submitted = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="lost_item_reports",
	)

	def __str__(self):
		return self.item_name
