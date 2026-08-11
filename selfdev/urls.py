"""
Root URL configuration for selfdev project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('workouts/', include('workouts.urls')),
    path('nutrition/', include('nutrition.urls')),
    path('mind/', include('mind.urls')),
    path('learning/', include('learning.urls')),
    path('career/', include('career.urls')),
    path('habits/', include('habits.urls')),
    path('goals/', include('growth.urls')),
    path('skills-trade/', include('skills_trade.urls')),
    path('progress/', include('progress.urls')),
    path('coach/', include('coach.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
