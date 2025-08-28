from django.urls import path
from . import views

app_name = 'branding'

urlpatterns = [
    path('edit/', views.edit_branding, name='edit_branding'),
]
