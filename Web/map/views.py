from django.shortcuts import render
import folium
from folium.plugins import HeatMap
import numpy as np
import scipy.spatial as spatial
import json
from geotargeting.models import Point
import pandas as pd

from matplotlib import pyplot as plt


def index(request):
    points = Point.objects.all()
    folium_map = folium.Map(width=800, height=500, location=[55.7558, 37.6173],
                            zoom_start=10, min_zoom=5)

    maximum = np.array([[val["count"], val["radius_area"]] for val in list(points.values())]).max(axis=0)
    dataHM = []
    for point in points:
        coordinates = json.loads(point.central_point)
        for val in point.under_point.split(';'):
            val = json.loads(val)
            dataHM.append([val[1], val[0], 5])
        # folium.Circle(location=[coordinates[1], coordinates[0]],
        #               radius=point.radius_area, color='red').add_to(folium_map)
        dataHM.append([coordinates[1], coordinates[0], 20 * point.radius_area / maximum[1] * point.count / maximum[0]])

    dataHM = pd.DataFrame(dataHM, columns=["lat", "lon", "count"])
    # HeatMap(data=dataHM.values.tolist(), radius=8, max_zoom=4).add_to(folium_map)

    radius = 0.15
    tree = spatial.KDTree(dataHM[["lat", "lon"]])
    neighbors = tree.query_ball_tree(tree, radius)
    x = [i for i in range(len(neighbors))]
    y = [len(neighbors[i]) for i in range(len(neighbors))]
    # y = sorted(y)
    plt.plot(x, y)
    plt.show()

    for i, val in enumerate(y):
        if val > 250:
            index = np.random.choice(neighbors[i])
            coord = dataHM.iloc[index]
            folium.CircleMarker(location=[coord[0], coord[1]],
                                radius=1, color='red').add_to(folium_map)

    folium_map = folium_map._repr_html_()
    context = {
        'map': folium_map,
    }

    return render(request, 'map/main.html', context)
