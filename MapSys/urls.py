from django.urls import path

from . import views

app_name = 'MapSys'
urlpatterns = [
    path('', views.index, name='index'),
]
