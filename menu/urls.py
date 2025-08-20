from django.urls import path
from .views import (
    ItemDashboardView,
    ItemCreateView,
    ItemUpdateView,
    item_delete_view
)

app_name = 'menu'

urlpatterns = [
    path('item_dashboard/', ItemDashboardView.as_view(), name='item_dashboard'),
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/edit/', ItemUpdateView.as_view(), name='item_update'),
    path('item/<int:pk>/delete/', item_delete_view, name='item_delete'),
]
