from django.db import models


# Create your models here.
class Producto(models.Model):
    name = models.TextField()
    sended = models.BooleanField(default=False)
    updated_at = models.DateTimeField(null=True)
    tienda = models.TextField(default='caracol')
    precio = models.TextField(null=True)

    def __str__(self):
        return self.name
