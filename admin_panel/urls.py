from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('users/', views.users_list, name='users_list'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),  # NEW
    path('tickets/<int:ticket_id>/update/', views.update_ticket_status, name='update_ticket'),
    path('tickets/<int:ticket_id>/add-note/', views.add_ticket_note, name='add_ticket_note'),  # NEW
    path('tickets/<int:ticket_id>/delete/', views.delete_ticket, name='delete_ticket'),
]