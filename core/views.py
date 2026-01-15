from django.shortcuts import render
from .models import Product, Alert
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    return render(request, 'home.html')

def dashboard(request):
    alerts = Alert.objects.order_by('-created_at')[:5]
    print("ALERT COUNT:", alerts.count())  # DEBUG LINE

    context = {
        'alerts': alerts,
    }

    return render(request, 'dashboard.html', context)

@csrf_exempt
def create_alert_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            message = data.get("message")
            source = data.get("source", "external")

            if not message:
                return JsonResponse(
                    {"error": "Message is required"},
                    status=400
                )

            alert = Alert.objects.create(
                message=message,
                source=source
            )

            return JsonResponse(
                {
                    "status": "success",
                    "alert_id": alert.id
                },
                status=201
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )

    return JsonResponse(
        {"error": "Only POST method allowed"},
        status=405
    )
