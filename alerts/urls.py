from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# REST API router
router = DefaultRouter()
router.register('alerts', views.AlertViewSet, basename='alert')
router.register('weather-events', views.WeatherEventViewSet, basename='weather-event')
router.register('trucks', views.TruckViewSet, basename='truck')

urlpatterns = [
    # REST API
    path('api/', include(router.urls)),
    
    # HTMX Dashboard
    path('', views.dashboard, name='dashboard'),
    path('htmx/alerts/', views.alert_list, name='alert-list'),
    path('htmx/alerts/<int:alert_id>/acknowledge/', views.acknowledge_alert_htmx, name='acknowledge-alert'),
]