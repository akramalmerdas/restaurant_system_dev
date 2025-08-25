from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('ws/connect/', views.ws_connect, name='ws_connect'),
]
