from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import NotebookEntryForm
from django.shortcuts import redirect


from .models import Alert
from .ai_engine import (
    generate_alert_intelligence,
    generate_daily_intelligence,
    generate_alert_trends,
)



def home(request):
    return render(request, "home.html")


from .ai_engine import generate_daily_intelligence
from .models import Alert

def dashboard(request):
    from .ai_engine import generate_financial_trend_alert
    generate_financial_trend_alert()

    alerts = Alert.objects.filter(resolved=False).order_by("-created_at")[:20]

    daily_intelligence = generate_daily_intelligence()
    trend_intelligence = generate_alert_trends()

    context = {
        "alerts": alerts,
        **daily_intelligence,
        **trend_intelligence,
    }

    return render(request, "dashboard.html", context)
def add_notebook_entry(request):
    """
    Phase 4.2 — User-facing notebook entry creation
    """

    if request.method == "POST":
        form = NotebookEntryForm(request.POST)
        if form.is_valid():
          entry = form.save()

         # Phase 4.4 — Financial anomaly check
        from .ai_engine import generate_financial_alert
        generate_financial_alert(entry)

        return redirect("core:dashboard")

    else:
        form = NotebookEntryForm()

    return render(
        request,
        "add_notebook_entry.html",
        {"form": form}
    )



@csrf_exempt
def ingest_alert(request):
    """
    External Alert Ingestion API (Phase 2)
    """
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)

        message = data.get("message")
        source = data.get("source", "external")

        if not message:
            return JsonResponse(
                {"error": "message is required"},
                status=400
            )

        # AI reasoning
        priority, explanation = generate_alert_intelligence(message)

        # Create alert with intelligence
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
