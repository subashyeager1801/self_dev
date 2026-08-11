"""Skills Trade URL configuration."""
from django.urls import path
from . import views

app_name = 'skills_trade'

urlpatterns = [
    path('', views.marketplace_view, name='marketplace'),
    path('api/create-listing/', views.create_listing_api, name='create_listing'),
    path('api/send-request/', views.send_trade_request_api, name='send_request'),
]
