from django.urls import path
from .views import (
    # ItemListView, # Remove or comment out if ItemDashboardView replaces it
    ItemDashboardView, # Import the new dashboard view
    ItemCreateView,
    ItemUpdateView,
    item_delete_view
)

app_name = 'item' # Namespace for URLs

urlpatterns = [
    # URL for the new item dashboard (replaces the old item_list if desired)
    path('item_dashboard/', ItemDashboardView.as_view(), name='item_dashboard'),

    # Keep the CRUD URLs
    path('new/', ItemCreateView.as_view(), name='item_create'), # e.g., /items/new/
    path('<int:pk>/edit/', ItemUpdateView.as_view(), name='item_update'), # e.g., /items/5/edit/
    path('item/<int:pk>/delete/', item_delete_view, name='item_delete'), # e.g., /items/5/delete/

    # Optional: If you still need the old simple list view, keep its URL
    # path('', ItemListView.as_view(), name='item_list'),
]