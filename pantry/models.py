from django.db import models

# Create your models here.
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    added_date = models.DateTimeField(auto_now_add=True)
    exp_date = models.DateTimeField()
    def __str__(self):
        return self.name