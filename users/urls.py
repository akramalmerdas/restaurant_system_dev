from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('customer_signup/', views.customerSignup, name='customer_signup'),
    path('profile/', views.customerProfile, name='customer_profile'),
]
