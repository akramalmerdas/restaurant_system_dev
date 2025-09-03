from django.urls import path
from . import views

app_name = 'theme'

urlpatterns = [
    path('edit/', views.edit_branding, name='edit_branding'),
    path('restore/', views.restore_default_branding, name='restore_default_branding'),
]
