# recipes/models.py
from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=255)
    ingredients = models.TextField()
    description = models.TextField()

    def __str__(self):
        return self.name
