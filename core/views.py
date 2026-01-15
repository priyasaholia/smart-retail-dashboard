from django.shortcuts import render
from .models import Product, Alert
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .ai_engine import generate_alert_intelligence



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
                    {"error": "message is required"},
                    status=400
                )

            # 🔥 THIS IS WHERE AI LOGIC GOES
            priority, explanation = generate_alert_intelligence(message)

            # 🔥 ALERT CREATION WITH INTELLIGENCE
            alert = Alert.objects.create(
                message=message,
                source=source,
                priority=priority,
                ai_explanation=explanation
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

