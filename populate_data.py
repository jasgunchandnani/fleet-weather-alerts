import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from alerts.models import Driver, Truck, WeatherEvent, Alert
from alerts.services import generate_alerts_for_event
from django.utils import timezone
from datetime import timedelta

print("🚀 Starting data population...")

# Create users and drivers
print("\n📋 Creating drivers...")
users_data = [
    {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'phone': '+1-555-0101'},
    {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'phone': '+1-555-0102'},
    {'username': 'bob_wilson', 'first_name': 'Bob', 'last_name': 'Wilson', 'phone': '+1-555-0103'},
    {'username': 'alice_jones', 'first_name': 'Alice', 'last_name': 'Jones', 'phone': '+1-555-0104'},
]

drivers = []
for data in users_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'first_name': data['first_name'],
            'last_name': data['last_name']
        }
    )
    driver, created = Driver.objects.get_or_create(
        user=user,
        defaults={'phone_number': data['phone']}
    )
    drivers.append(driver)
    print(f"  ✓ Driver: {driver.user.get_full_name()}")

# Create trucks with GPS locations
print("\n🚛 Creating trucks...")
trucks_data = [
    {'plate': 'TX-1234', 'lat': 29.7604, 'lon': -95.3698, 'driver': drivers[0]},  # Houston
    {'plate': 'CA-5678', 'lat': 34.0522, 'lon': -118.2437, 'driver': drivers[1]},  # Los Angeles
    {'plate': 'NY-9012', 'lat': 40.7128, 'lon': -74.0060, 'driver': drivers[2]},  # New York
    {'plate': 'FL-3456', 'lat': 25.7617, 'lon': -80.1918, 'driver': drivers[3]},  # Miami
    {'plate': 'TX-7890', 'lat': 29.4241, 'lon': -98.4936, 'driver': drivers[0]},  # San Antonio
]

trucks = []
for data in trucks_data:
    truck, created = Truck.objects.get_or_create(
        license_plate=data['plate'],
        defaults={
            'current_lat': data['lat'],
            'current_lon': data['lon'],
            'current_driver': data['driver']
        }
    )
    trucks.append(truck)
    print(f"  ✓ Truck: {truck.license_plate} @ ({truck.current_lat}, {truck.current_lon})")

# Create weather events
print("\n🌩️  Creating weather events...")
events_data = [
    {
        'type': 'storm',
        'severity': 'severe',
        'location': 'Houston Metro Area',
        'lat': 29.7604,
        'lon': -95.3698,
        'radius': 40,
        'description': 'Severe thunderstorm with heavy rain, lightning, and winds up to 60mph. Flash flooding possible in low-lying areas. Avoid unnecessary travel.'
    },
    {
        'type': 'flood',
        'severity': 'high',
        'location': 'Miami-Dade County',
        'lat': 25.7617,
        'lon': -80.1918,
        'radius': 35,
        'description': 'Flash flood warning in effect. Multiple road closures reported. Do not attempt to drive through flooded areas. Turn around, don\'t drown.'
    },
    {
        'type': 'fog',
        'severity': 'moderate',
        'location': 'Los Angeles Basin',
        'lat': 34.0522,
        'lon': -118.2437,
        'radius': 25,
        'description': 'Dense fog reducing visibility to less than 200 meters. Reduce speed and use low-beam headlights. Increase following distance.'
    },
    {
        'type': 'ice',
        'severity': 'high',
        'location': 'New York Tri-State Area',
        'lat': 40.7128,
        'lon': -74.0060,
        'radius': 50,
        'description': 'Freezing rain creating dangerous ice conditions on roads and bridges. Multiple accidents reported. Drive at reduced speeds, use extreme caution.'
    },
]

for data in events_data:
    event, created = WeatherEvent.objects.get_or_create(
        location_name=data['location'],
        event_type=data['type'],
        defaults={
            'severity': data['severity'],
            'center_lat': data['lat'],
            'center_lon': data['lon'],
            'radius_km': data['radius'],
            'description': data['description'],
            'start_time': timezone.now(),
            'is_active': True
        }
    )
    
    if created:
        print(f"  ✓ Event: {event.get_event_type_display()} - {event.location_name}")
        
        # Generate alerts for this event
        count = generate_alerts_for_event(event.id)
        print(f"    → Generated {count} alert(s)")
    else:
        print(f"  ⚠ Event already exists: {event.location_name}")

print("\n✅ Data population complete!")
print("\n📊 Summary:")
print(f"   - Drivers: {Driver.objects.count()}")
print(f"   - Trucks: {Truck.objects.count()}")
print(f"   - Weather Events: {WeatherEvent.objects.count()}")
print(f"   - Alerts: {Alert.objects.count()}")
print("\n🌐 You can now:")
print("   1. Visit http://localhost:8000 for the dashboard")
print("   2. Visit http://localhost:8000/admin for the admin panel")
print("   3. Visit http://localhost:8000/api/alerts/ for the API")