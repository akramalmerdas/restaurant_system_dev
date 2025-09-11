from django.urls import path
from . import views

app_name = 'theme'

urlpatterns = [
    path('manage/', views.manage_branding, name='manage_branding'),
    path('create/', views.create_branding, name='create_branding'),
    path('edit/<int:profile_id>/', views.edit_branding, name='edit_branding'),
    path('delete/<int:profile_id>/', views.delete_branding, name='delete_branding'),
    path('set-active/<int:profile_id>/', views.set_active_branding, name='set_active_branding'),
    path('edit/', views.edit_branding, name='edit_branding_active'),
    path('restore/', views.restore_default_branding, name='restore_default_branding'),
]
