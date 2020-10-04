from django.urls import path
from . import views
from geotargeting import views as geoView

urlpatterns = [
    path('', views.index),
    path('api/', geoView.GeoView.as_view()),
]