from django.shortcuts import render
import folium
from folium import plugins
import numpy as np


def get_distanse(lat1, lat2, lon1, lon2):
    R = 6371
    sin1 = np.sin((lat1 - lat2) / 2)
    sin2 = np.sin((lon1 - lon2) / 2)
    return 2 * R * np.arcsin(np.sqrt(sin1 * sin1 + sin2 * sin2 * np.cos(lat1) * np.cos(lat2)))


def index(request):
    folium_map = folium.Map(width=800, height=500, location=[55.7558, 37.6173],
                            zoom_start=10, min_zoom=5)
    folium_map = folium_map._repr_html_()
    context = {
        'map': folium_map,
    }
    return render(request, 'map/main.html', context)
