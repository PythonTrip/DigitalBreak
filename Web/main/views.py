from django.shortcuts import render
from django.shortcuts import render, redirect
import pandas as pd


def update(request):
    data = pd.read_csv('geotargeting\\people.csv', encoding='cp1251')
    return redirect(index)


def index(request):
    return render(request, 'main/index.html')
