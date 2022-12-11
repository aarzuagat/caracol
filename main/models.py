from django.db import models


# Create your models here.
class Producto(models.Model):
    name = models.TextField()
    sended = models.BooleanField(default=False)

    def __str__(self):
        return self.name
