from django.shortcuts import render
from .models import Product, Alert

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    alerts = Alert.objects.order_by('-created_at')[:5]
    print("ALERT COUNT:", alerts.count())  # DEBUG LINE

    context = {
        'alerts': alerts,
    }

    return render(request, 'dashboard.html', context)

