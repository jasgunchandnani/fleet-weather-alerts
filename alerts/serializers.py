from rest_framework import serializers
from .models import Alert, Truck, Driver, WeatherEvent

class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model with related data"""
    truck_plate = serializers.CharField(source='truck.license_plate', read_only=True)
    driver_name = serializers.CharField(source='driver.user.get_full_name', read_only=True)
    event_type = serializers.CharField(source='weather_event.get_event_type_display', read_only=True)
    event_severity = serializers.CharField(source='weather_event.get_severity_display', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'truck_plate', 'driver_name', 'event_type', 'event_severity',
            'priority', 'status', 'title', 'message', 
            'created_at', 'acknowledged_at'
        ]

class WeatherEventSerializer(serializers.ModelSerializer):
    """Serializer for WeatherEvent model"""
    class Meta:
        model = WeatherEvent
        fields = '__all__'

class TruckSerializer(serializers.ModelSerializer):
    """Serializer for Truck model"""
    driver_name = serializers.CharField(source='current_driver.user.get_full_name', read_only=True)
    
    class Meta:
        model = Truck
        fields = ['id', 'license_plate', 'driver_name', 'current_lat', 'current_lon', 'is_active']