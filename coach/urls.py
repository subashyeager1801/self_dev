"""Coach URL configuration."""
from django.urls import path
from . import views

app_name = 'coach'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('daily/', views.daily_coaching_view, name='daily'),
    path('memory/', views.memory_view, name='memory'),
    path('api/send/', views.send_message_api, name='send_message'),
    path('api/memory/', views.manage_memory_api, name='manage_memory'),
]
