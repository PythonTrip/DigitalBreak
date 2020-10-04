from django.shortcuts import render
from django.shortcuts import render, redirect
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from geotargeting.models import Point, Place
import numpy as np
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from geotargeting.serializers import PointSerializer
from matplotlib import pyplot as plt
import folium
from folium import plugins
import scipy.spatial as spatial


def get_distanse(lat1, lat2, lon1, lon2):
    R = 6371
    sin1 = np.sin((lat1 - lat2) / 2)
    sin2 = np.sin((lon1 - lon2) / 2)
    return 2 * R * np.arcsin(np.sqrt(sin1 * sin1 + sin2 * sin2 * np.cos(lat1) * np.cos(lat2)))


def get_yandex_data(name, count):
    response = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=51389b56-79d7-42fa-a04e-c2c634edf11f&"
                            f"geocode={name}&"
                            f"format=xml")
    root = ET.fromstring(response.content)
    for points in zip(
            root.iter("{http://www.opengis.net/gml}lowerCorner"),
            root.iter("{http://www.opengis.net/gml}upperCorner"),
            root.iter("{http://www.opengis.net/gml}pos")
    ):
        data = []
        for point in points:
            data.append([float(x) for x in point.text.split(' ')])
        break

    Point(
        name=name,
        central_point=str(data[2]),
        under_point=str(data[0]) + ";" + str(data[1]),
        radius_area=get_distanse(data[0][0], data[1][0], data[0][1], data[1][1]) / 2,
        count=count
    ).save()


def index(request):
    return render(request, 'main/index.html')


class UpdateView(APIView):
    @staticmethod
    def get(request):
        points = Point.objects.all()
        points_serialize = PointSerializer(points, many=True)
        return Response(
            {
                "points": points_serialize.data,
            })

    def post(self, request):
        update = request.data.get('update')
        settings = {
            "radius": 0.05,
            "val": 40
        }
        if "settings" in update.keys():
            settings = update["settings"]

        if update["status"] == 1:
            data = pd.read_csv('geotargeting\\people.csv', encoding='cp1251')
            for name, count in data.values:
                get_yandex_data("Москва, " + name, float(count))

        elif update["status"] == 2:
            for i in range(1, 6):
                data = pd.read_excel(f"geotargeting\\files\\{i}.xlsx", encoding='cp1251')
                geodata = [x.split("coordinates=")[1].split("}")[0]
                           for x in data["geoData"][:100]]
                for obj in geodata:
                    Place(
                        central_point=str(obj),
                        temp=i * 2
                    ).save()
        else:
            points = Point.objects.all()
            folium_map = folium.Map(location=[55.7558, 37.6173],
                                    zoom_start=10, min_zoom=5)

            fg = folium.FeatureGroup(name='Банкоматы', show=True)
            fg.add_to(folium_map)

            fg2 = folium.FeatureGroup(name='Тепловая карта', show=True)
            hm_cluster = plugins.MarkerCluster().add_to(fg2)
            folium_map.add_child(fg2)

            folium.LayerControl().add_to(folium_map)
            maximum = np.array([[val["count"], val["radius_area"]] for val in list(points.values())]).max(axis=0)
            dataHM = []
            for point in points:
                coordinates = json.loads(point.central_point)
                for val in point.under_point.split(';'):
                    val = json.loads(val)
                    dataHM.append([val[1], val[0], 5])
                # folium.Circle(location=[coordinates[1], coordinates[0]],
                #               radius=point.radius_area, color='red').add_to(folium_map)
                dataHM.append(
                    [coordinates[1], coordinates[0], 30 * point.radius_area / maximum[1] * point.count / maximum[0]])

            places = Place.objects.all()
            dataPl = []
            for place in places:
                coordinates = json.loads(place.central_point)
                dataPl.append([coordinates[1], coordinates[0], place.temp])

            dataHM = pd.DataFrame(dataHM, columns=["lat", "lon", "count"])
            plugins.HeatMap(data=(dataHM.values.tolist() + dataPl), radius=10, max_zoom=4).add_to(hm_cluster)

            radius = settings["radius"]
            tree = spatial.KDTree(dataHM[["lat", "lon"]])
            neighbors = tree.query_ball_tree(tree, radius)
            x = [i for i in range(len(neighbors))]
            y = [len(neighbors[i]) for i in range(len(neighbors))]
            y = sorted(y)
            plt.plot(x, y)
            plt.show()

            for i, val in enumerate(y):
                if val > settings["val"]:
                    min_dist = 10000000
                    output_coord = []
                    for ind in neighbors[i]:
                        coord = dataHM.iloc[ind]
                        if 55.6 < coord[0] < 55.71 and 37.5 < coord[1] < 37.7:
                            for pl in dataPl:
                                if 55.6 < pl[0] < 55.71 and 37.5 < pl[1] < 37.7:
                                    if get_distanse(coord[0], pl[0], coord[1], pl[1]) < min_dist:
                                        min_dist = get_distanse(coord[0], pl[0], coord[1], pl[1])
                                        output_coord = coord

                    if len(output_coord) > 1:
                        folium.CircleMarker(location=[output_coord[0], output_coord[1]],
                                            radius=3, color='red').add_to(fg)
                    # coord = dataHM.iloc[index]
                    # if 55.6 < coord[0] < 55.71 and 37.5 < coord[1] < 37.7:
                    #     folium.CircleMarker(location=[coord[0], coord[1]],
                    #                         radius=3, color='green').add_to(fg)

                index = np.random.choice(neighbors[i])
                coord = dataHM.iloc[index]
                if 55.6 < coord[0] < 55.71 and 37.5 < coord[1] < 37.7:
                    folium.CircleMarker(location=[coord[0], coord[1]],
                                        radius=3, color='green').add_to(fg)
            folium_map.save(".\\map\\templates\\map\\map.html")

        return Response({"success": "Update successfully"})
