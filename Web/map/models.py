from django.db import models


# Create your models here.
class Point(models.Model):
    coord = models.TextField('coordinates', null=True)

    def __str__(self):
        return f"Координаты {self.coord}"

    class Meta:
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'
