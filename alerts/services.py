from .models import Alert, Truck, WeatherEvent
from django.utils import timezone
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def classify_alert_priority(weather_event, distance_km):
    """
    Determine if alert should be critical or standard
    
    Business Rules:
    - Severe weather = always critical
    - High severity within 20km = critical
    - Flood/Storm within 10km = critical
    - Everything else = standard
    """
    # Rule 1: Severe events are always critical
    if weather_event.severity == 'severe':
        return Alert.PRIORITY_CRITICAL
    
    # Rule 2: High severity close by
    if weather_event.severity == 'high' and distance_km < 20:
        return Alert.PRIORITY_CRITICAL
    
    # Rule 3: Dangerous event types close by
    if weather_event.event_type in ['flood', 'storm', 'ice'] and distance_km < 10:
        return Alert.PRIORITY_CRITICAL
    
    # Default to standard
    return Alert.PRIORITY_STANDARD

def generate_message(weather_event, priority, distance_km):
    """Create alert title and message based on priority"""
    if priority == Alert.PRIORITY_CRITICAL:
        title = f"⚠️ CRITICAL: {weather_event.get_event_type_display()}"
        message = f"{weather_event.description}\n\n"
        message += f"Distance: {distance_km:.1f}km from your location.\n"
        message += f"IMMEDIATE ACTION REQUIRED - Contact dispatch."
    else:
        title = f"Weather Advisory: {weather_event.get_event_type_display()}"
        message = f"{weather_event.description}\n\n"
        message += f"Distance: {distance_km:.1f}km from your location.\n"
        message += f"Monitor conditions and adjust route if necessary."
    
    return title, message

def generate_alerts_for_event(weather_event_id):
    """
    Main function: Generate alerts for all trucks affected by weather event
    Called automatically when weather event is created
    """
    try:
        event = WeatherEvent.objects.get(id=weather_event_id)
    except WeatherEvent.DoesNotExist:
        print(f"Weather event {weather_event_id} not found")
        return 0
    
    # Find all active trucks with valid GPS coordinates
    active_trucks = Truck.objects.filter(
        is_active=True,
        current_lat__isnull=False,
        current_lon__isnull=False,
        current_driver__isnull=False  # Must have a driver
    )
    
    alerts_created = 0
    
    for truck in active_trucks:
        # Calculate distance between truck and event center
        distance = calculate_distance(
            truck.current_lat, truck.current_lon,
            event.center_lat, event.center_lon
        )
        
        # Skip if truck is outside affected radius
        if distance > event.radius_km:
            continue
        
        # Check if alert already exists (prevent duplicates)
        if Alert.objects.filter(weather_event=event, truck=truck).exists():
            print(f"Alert already exists for truck {truck.license_plate}")
            continue
        
        # Classify priority based on severity and distance
        priority = classify_alert_priority(event, distance)
        
        # Generate message
        title, message = generate_message(event, priority, distance)
        
        # Create alert
        alert = Alert.objects.create(
            weather_event=event,
            truck=truck,
            driver=truck.current_driver,
            priority=priority,
            status='pending',
            title=title,
            message=message
        )
        
        alerts_created += 1
        print(f"✓ Alert {alert.id} created: {priority} for truck {truck.license_plate}")
    
    print(f"Total alerts created: {alerts_created}")
    return alerts_created