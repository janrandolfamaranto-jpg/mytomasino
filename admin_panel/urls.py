from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('users/', views.users_list, name='users_list'),
]
