from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event/<int:pk>/register/', views.event_register, name='event_register'),
    path('event/<int:pk>/unregister/', views.event_unregister, name='event_unregister'),
    path('my-registrations/', views.user_registrations, name='user_registrations'),
    path('my-events/', views.organizer_events, name='organizer_events'),
    path('deleted-events/', views.deleted_events, name='deleted_events'),
    path('event/<int:pk>/restore/', views.event_restore, name='event_restore'),
    path('event/<int:event_id>/unregister-user/<int:registration_id>/', views.admin_unregister_user, name='admin_unregister_user'),
    path('event/<int:pk>/register-user/<int:registration_pk>/', views.admin_register_user, name='admin_register_user'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('api/calendar-events/', views.calendar_events, name='calendar_events'),
]
