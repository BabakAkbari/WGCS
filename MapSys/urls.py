from django.urls import path

from . import views

app_name = 'MapSys'
urlpatterns = [
    path('', views.index, name='index'),
    path('getloc', views.getloc, name='getloc'),
    path('getyaw', views.getyaw, name='getyaw'),
    path('connect', views.connect, name='connect'),
    path('getstatus', views.getstatus, name='getstatus'),
    path('startmission', views.startmission, name='startmission'),
    path('uploadpoints', views.uploadpoints, name='uploadpoints'),
]
