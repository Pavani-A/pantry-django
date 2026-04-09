from django.db import models

# Create your models here.
from django.db import models

from django.contrib.auth.models import User

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ NEW
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    added_date = models.DateTimeField(auto_now_add=True)
    exp_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name