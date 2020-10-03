from django.shortcuts import render
from django.shortcuts import render, redirect
import pandas as pd
import requests
import xml.etree.ElementTree as ET


def get_yandex_data(name):
    response = requests.get(f"https://geocode-maps.yandex.ru/1.x/?apikey=51389b56-79d7-42fa-a04e-c2c634edf11f&"
                            f"geocode={name}&"
                            f"format=xml")
    root = ET.fromstring(response.content)
    for low, up, pos in zip(
            root.iter("{http://www.opengis.net/gml}lowerCorner"),
            root.iter("{http://www.opengis.net/gml}upperCorner"),
            root.iter("{http://www.opengis.net/gml}pos")
    ):
        print(low, up, pos)


def update(request):
    data = pd.read_csv('geotargeting\\people.csv', encoding='cp1251')
    for name, count in data.values:
        get_yandex_data("Москва, " + name)
    return redirect(index)


def index(request):
    return render(request, 'main/index.html')
