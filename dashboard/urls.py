from django.urls import path
from . import views

app_name = 'dashboard'


urlpatterns = [
    path('', views.dashboard_home, name='home'),  
    path('history/', views.history_view, name='history'),
    path('settings/', views.settings_view, name='settings'),    
]

