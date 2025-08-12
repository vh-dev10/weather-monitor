from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_monitor_main,name="weather"),
]