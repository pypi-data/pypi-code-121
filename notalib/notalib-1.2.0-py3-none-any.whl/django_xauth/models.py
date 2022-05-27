from django.db import models

class Nothing(models.Model):
	pass

	class Meta:
		managed = False
