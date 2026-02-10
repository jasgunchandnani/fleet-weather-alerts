from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Alert, WeatherEvent, Truck
from .serializers import AlertSerializer, WeatherEventSerializer, TruckSerializer
from .services import generate_alerts_for_event

# ===== REST API VIEWS =====

class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing and acknowledging alerts"""
    queryset = Alert.objects.select_related('truck', 'driver', 'weather_event').all()
    serializer_class = AlertSerializer
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a specific alert"""
        alert = self.get_object()
        
        if alert.status == 'acknowledged':
            return Response({
                'status': 'already_acknowledged',
                'message': 'Alert was already acknowledged'
            })
        
        alert.status = 'acknowledged'
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'success',
            'message': 'Alert acknowledged successfully',
            'data': AlertSerializer(alert).data
        })
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get only critical unacknowledged alerts"""
        alerts = self.queryset.filter(
            priority='critical',
            status__in=['pending', 'delivered']
        )
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

class WeatherEventViewSet(viewsets.ModelViewSet):
    """API endpoint for weather events"""
    queryset = WeatherEvent.objects.all()
    serializer_class = WeatherEventSerializer
    
    def create(self, request, *args, **kwargs):
        """Create weather event and auto-generate alerts"""
        response = super().create(request, *args, **kwargs)
        
        # Automatically generate alerts for this event
        event_id = response.data['id']
        alerts_count = generate_alerts_for_event(event_id)
        
        # Add count to response
        response.data['alerts_generated'] = alerts_count
        
        return response

class TruckViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing trucks"""
    queryset = Truck.objects.select_related('current_driver').all()
    serializer_class = TruckSerializer


# ===== HTMX VIEWS =====

def dashboard(request):
    """Main dashboard page"""
    context = {
        'total_alerts': Alert.objects.count(),
        'critical_alerts': Alert.objects.filter(priority='critical', status__in=['pending', 'delivered']).count(),
        'active_trucks': Truck.objects.filter(is_active=True).count(),
    }
    return render(request, 'alerts/dashboard.html', context)

def alert_list(request):
    """HTMX partial: Returns alert list HTML"""
    priority = request.GET.get('priority', 'all')
    
    # Base queryset
    alerts = Alert.objects.select_related('truck', 'driver', 'weather_event')
    
    # Filter by priority if specified
    if priority != 'all':
        alerts = alerts.filter(priority=priority)
    
    # Limit to recent alerts
    alerts = alerts[:50]
    
    return render(request, 'alerts/partials/alert_list.html', {
        'alerts': alerts
    })

@api_view(['POST'])
def acknowledge_alert_htmx(request, alert_id):
    """HTMX endpoint: Acknowledge alert and return updated card"""
    alert = get_object_or_404(Alert, id=alert_id)
    
    alert.status = 'acknowledged'
    alert.acknowledged_at = timezone.now()
    alert.save()
    
    # Return updated alert card HTML
    return render(request, 'alerts/partials/alert_card.html', {
        'alert': alert
    })