from django.shortcuts import render
from django.shortcuts import render, redirect
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from geotargeting.models import Point
import numpy as np


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


def update(request):
    data = pd.read_csv('geotargeting\\people.csv', encoding='cp1251')
    print(len(data.values))
    for name, count in data.values:
        get_yandex_data("Москва, " + name, float(count))
    return redirect(index)


def index(request):
    return render(request, 'main/index.html')
