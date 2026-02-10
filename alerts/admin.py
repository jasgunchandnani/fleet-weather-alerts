from django.contrib import admin
from .models import Driver, Truck, WeatherEvent, Alert

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone_number']

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'current_driver', 'current_lat', 'current_lon', 'is_active', 'last_update']
    list_filter = ['is_active']
    search_fields = ['license_plate']

@admin.register(WeatherEvent)
class WeatherEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'severity', 'location_name', 'start_time', 'is_active']
    list_filter = ['event_type', 'severity', 'is_active']
    search_fields = ['location_name', 'description']
    date_hierarchy = 'start_time'

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['truck', 'priority', 'status', 'created_at', 'acknowledged_at']
    list_filter = ['priority', 'status', 'weather_event__event_type']
    search_fields = ['truck__license_plate', 'driver__user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']