from django.db import models

# Create your models here.
class package(models.Model):
    place = models.CharField(max_length=200, null=True)
    desc = models.CharField(max_length=200, null=True)
    img = models.CharField(max_length=200, null=True)
