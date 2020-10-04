from django.db import models


# Create your models here.
class Point(models.Model):
    """Точки"""
    name = models.CharField("Name", max_length=100)
    central_point = models.TextField('coordinates', null=True)
    under_point = models.TextField('under coordinates', null=True)
    radius_area = models.FloatField('radius')
    count = models.FloatField('Count')

    def __str__(self):
        return f"Координаты {self.name}"

    class Meta:
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'


class Place(models.Model):
    """Точки"""
    central_point = models.TextField('coordinates', null=True)
    temp = models.IntegerField()
