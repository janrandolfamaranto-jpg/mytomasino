from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='ticket_overview'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
]
