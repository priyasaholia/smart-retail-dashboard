from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from .ai_engine import generate_notebook_observations, get_entry_intelligence_markers


from .models import Alert, NotebookEntry
from .forms import NotebookEntryForm
from .ai_engine import (
    generate_alert_intelligence,
    generate_daily_intelligence,
    generate_alert_trends,
    generate_financial_baseline,
    generate_financial_trends,
    generate_financial_trend_alert,
    generate_financial_alert,
)

# ----------------------------
# BASIC VIEWS
# ----------------------------

def home(request):
    return render(request, "home.html")


# ----------------------------
# DASHBOARD (COMMAND CENTER)
# ----------------------------

from .models import Alert, NotebookEntry
from .ai_engine import (
    generate_daily_intelligence,
    generate_alert_trends,
    generate_financial_baseline,
    generate_financial_trends,
    generate_financial_trend_alert,
)

@login_required
def dashboard(request):
    alerts = Alert.objects.filter(resolved=False).order_by("-created_at")[:20]
    notebook_entries = NotebookEntry.objects.all()

    has_alerts = alerts.exists()
    has_notebook = notebook_entries.exists()

    is_new_user = not (has_alerts or has_notebook)

    context = {
        "alerts": alerts,
        "is_new_user": is_new_user,
    }

    # 🔥 Only generate intelligence if system has data
    if not is_new_user:
        # Safe trigger (only meaningful when data exists)
        generate_financial_trend_alert()

        daily_intelligence = generate_daily_intelligence()
        trend_intelligence = generate_alert_trends()
        financial_baseline = generate_financial_baseline()
        financial_trends = generate_financial_trends()

        context.update({
            **daily_intelligence,
            **trend_intelligence,
            "financial_baseline": financial_baseline,
            "financial_trends": financial_trends,
        })

    return render(request, "dashboard.html", context)

# ----------------------------
# NOTEBOOK
# ----------------------------

def add_notebook_entry(request):
    """
    Phase 4.2 — User-facing notebook entry creation
    """

    if request.method == "POST":
        form = NotebookEntryForm(request.POST)

        if form.is_valid():
            entry = form.save()

            # Phase 4.4 — Financial anomaly detection
            generate_financial_alert(entry)

            return redirect("core:dashboard")

    else:
        form = NotebookEntryForm()

    return render(
        request,
        "add_notebook_entry.html",
        {"form": form}
    )


def view_notebook(request):
    """
    Prototype — View recent notebook entries with intelligence feedback
    """
    entries = NotebookEntry.objects.order_by("-created_at")[:20]
    observations = generate_notebook_observations()
    entry_markers = get_entry_intelligence_markers()

    context = {
        "entries": entries,
        "observations": observations,
        "entry_markers": entry_markers,
    }

    return render(
        request,
        "view_notebook.html",
        context
    )


# ----------------------------
# ALERT INGESTION API
# ----------------------------

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

        priority, explanation = generate_alert_intelligence(message)

        alert = Alert.objects.create(
            message=message,
            source=source,
            priority=priority,
            ai_explanation=explanation
        )

        return JsonResponse(
            {"status": "success", "alert_id": alert.id},
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )
@csrf_exempt
def copilot_ask(request):
    """
    Phase 6.4 — Copilot API endpoint
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST allowed"},
            status=405
        )

    try:
        data = json.loads(request.body)
        question = data.get("question")

        if not question:
            return JsonResponse(
                {"error": "Question is required"},
                status=400
            )

        from .ai_engine import generate_copilot_answer
        answer = generate_copilot_answer(question)

        return JsonResponse(
            {
                "question": question,
                "answer": answer
            }
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
