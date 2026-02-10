from django.db import models
from django.contrib.auth.models import User

class Driver(models.Model):
    """Truck driver information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.phone_number}"

class Truck(models.Model):
    """Fleet truck with GPS location"""
    license_plate = models.CharField(max_length=20, unique=True, db_index=True)
    current_driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)
    current_lat = models.FloatField(null=True, blank=True, help_text="Latitude")
    current_lon = models.FloatField(null=True, blank=True, help_text="Longitude")
    last_update = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.license_plate
    
    class Meta:
        ordering = ['license_plate']

class WeatherEvent(models.Model):
    """Weather event that affects trucks"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]
    
    EVENT_TYPES = [
        ('storm', 'Storm'),
        ('flood', 'Flood'),
        ('snow', 'Snowfall'),
        ('fog', 'Heavy Fog'),
        ('heat', 'Extreme Heat'),
        ('ice', 'Ice/Freezing'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    location_name = models.CharField(max_length=200)
    center_lat = models.FloatField(help_text="Center latitude")
    center_lon = models.FloatField(help_text="Center longitude")
    radius_km = models.FloatField(default=50, help_text="Affected radius in km")
    description = models.TextField()
    start_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.location_name}"
    
    class Meta:
        ordering = ['-start_time']

class Alert(models.Model):
    """Alert sent to driver about weather event"""
    PRIORITY_CRITICAL = 'critical'
    PRIORITY_STANDARD = 'standard'
    PRIORITY_CHOICES = [
        (PRIORITY_CRITICAL, 'Critical'),
        (PRIORITY_STANDARD, 'Standard'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('acknowledged', 'Acknowledged'),
    ]
    
    weather_event = models.ForeignKey(WeatherEvent, on_delete=models.CASCADE)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['weather_event', 'truck']  # Prevent duplicate alerts
    
    def __str__(self):
        return f"{self.priority.upper()}: {self.truck.license_plate}"