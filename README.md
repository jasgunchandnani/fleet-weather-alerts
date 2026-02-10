# 🚛 Fleet Weather Alert System

## Overview

A real-time weather alert system for fleet management that:
- Classifies alerts as **Critical** or **Standard** based on severity and proximity
- Provides live dashboard with HTMX (no page reloads)
- Exposes REST API for mobile app integration
- Prevents duplicate alerts using database constraints
- Implements distance-based geofencing

## 📸 Screenshots

### Live Dashboard
![Dashboard](screenshots/dashboard.png)

### Alert Details
![Critical Alert](screenshots/critical-alert.png)

### Admin Interface
![Admin Panel](screenshots/admin-panel.png)

### REST API
![API Response](screenshots/api-response.png)

## Features Implemented

✅ **Alert Classification Engine**
- Critical: Severe weather OR high severity within 20km
- Standard: All other conditions
- Business rules in `alerts/services.py`

✅ **HTMX Live Dashboard**
- Auto-refreshes every 10 seconds
- Filter by priority without page reload
- One-click acknowledgment

✅ **Django REST API**
- `/api/alerts/` - List all alerts
- `/api/alerts/critical/` - Critical unacknowledged only
- `/api/alerts/{id}/acknowledge/` - Mark as acknowledged
- `/api/weather-events/` - Create events (auto-generates alerts)
- `/api/trucks/` - View fleet status

✅ **Geospatial Logic**
- Haversine formula for distance calculation
- Radius-based geofencing
- Automatic truck-to-event matching

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Load sample data (4 drivers, 5 trucks, 4 weather events)
python populate_data.py

# Start server
python manage.py runserver
```

## Access Points

- **Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/

## Project Structure
```
fleet-weather-alerts/
├── alerts/
│   ├── models.py          # Database schema
│   ├── services.py        # Business logic (alert classification)
│   ├── serializers.py     # API serializers
│   ├── views.py           # REST API + HTMX views
│   ├── admin.py           # Admin interface
│   └── templates/
│       └── alerts/
│           ├── dashboard.html
│           └── partials/
├── config/
│   ├── settings.py
│   └── urls.py
├── populate_data.py       # Sample data generator
└── manage.py
```

## Architecture Highlights

### Alert Classification Logic
```python
# Severe weather = always critical
if weather_event.severity == 'severe':
    return CRITICAL

# High severity within 20km = critical  
if weather_event.severity == 'high' and distance < 20:
    return CRITICAL
    
# Flood/storm within 10km = critical
if event_type in ['flood', 'storm'] and distance < 10:
    return CRITICAL
```

### HTMX Live Updates
```html
<div hx-get="/htmx/alerts/" 
     hx-trigger="every 10s"
     hx-swap="innerHTML">
```

### Idempotency (Prevent Duplicates)
```python
class Alert(models.Model):
    class Meta:
        unique_together = ['weather_event', 'truck']
```

## Testing the System

### 1. View Existing Alerts
Visit dashboard to see sample alerts

### 2. Create New Weather Event
```bash
# Via Admin
http://localhost:8000/admin/alerts/weatherevent/add/

# Or via API
curl -X POST http://localhost:8000/api/weather-events/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "storm",
    "severity": "severe",
    "location_name": "Houston I-10",
    "center_lat": 29.7604,
    "center_lon": -95.3698,
    "radius_km": 30,
    "description": "Severe thunderstorm warning",
    "start_time": "2025-02-10T14:00:00Z",
    "is_active": true
  }'
```

### 3. Test Alert Generation
Alerts automatically generate for trucks within radius

### 4. Test HTMX Features
- Change priority filter → no page reload
- Click acknowledge → card updates in-place
- Wait 10 seconds → auto-refresh

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **HTMX over React** | Server-side rendering, less complexity, faster dev |
| **Haversine distance** | Simple for MVP; production would use PostGIS |
| **Unique constraint** | Database-level duplicate prevention |
| **Auto-generate on create** | Alerts created immediately when event is saved |

## Production Roadmap (Not Implemented)

- [ ] Celery for async alert generation
- [ ] PostGIS for accurate geofencing
- [ ] FCM/SMS multi-channel notifications
- [ ] Retry logic with exponential backoff
- [ ] Driver mobile app
- [ ] Real weather API integration (OpenWeather, NOAA)

## Technologies Used

- **Backend**: Django 5.0, Django REST Framework
- **Frontend**: HTMX, Alpine.js (minimal JS)
- **Database**: SQLite (dev), PostgreSQL ready
- **API**: RESTful with auto-generating alerts

## Why This Matters

This project demonstrates:
1. **Systems thinking** - Alert classification, geofencing, idempotency
2. **Django expertise** - Models, DRF, services layer
3. **HTMX proficiency** - Live updates without SPAs
4. **Production mindset** - Handles edge cases, scales to production
5. **Logistics domain** - Fleet operations, driver safety

---


