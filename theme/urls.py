from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.edit_branding, name='edit_branding'),
]
