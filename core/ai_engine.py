from datetime import date
from .models import Alert
def generate_alert_intelligence(message):
    text = message.lower()

    if "medicine" in text or "paracetamol" in text:
        return (
            "critical",
            "This alert involves an essential medical item. "
            "If unavailable, customers may be turned away, "
            "leading to trust loss and urgency-related impact."
        )

    if "low stock" in text:
        return (
            "medium",
            "Stock levels are running low. "
            "Repeated occurrences may affect availability and sales."
        )

    return (
        "low",
        "This alert does not indicate immediate customer impact, "
        "but should be monitored."
    )

from django.utils.timezone import now
from datetime import timedelta

def generate_daily_intelligence():
    """
    Phase 3.2 — Daily Executive Intelligence
    Backend truth aligned with dashboard UI
    """

    today = now().date()

    unresolved_alerts = Alert.objects.filter(resolved=False)
    alerts_today = unresolved_alerts.filter(created_at__date=today)
    resolved_today = Alert.objects.filter(
        resolved=True,
        created_at__date=today
    )

    critical_alerts = unresolved_alerts.filter(priority="critical")
    medium_alerts = unresolved_alerts.filter(priority="medium")

    total_unresolved = unresolved_alerts.count()
    critical_unresolved = critical_alerts.count()
    total_alerts_today = alerts_today.count()
    resolved_today_count = resolved_today.count()

    # --- Executive reasoning ---
    if critical_unresolved > 0:
        daily_summary = f"{critical_unresolved} critical issue(s) require immediate attention."
        daily_insight = (
            "These issues may impact customer trust, essential product availability, "
            "or revenue if not resolved today."
        )
        needs_attention = True
    elif medium_alerts.exists():
        daily_summary = "Operational issues detected that need review."
        daily_insight = (
            "While not immediately critical, these issues may escalate "
            "if corrective action is delayed."
        )
        needs_attention = True
    else:
        daily_summary = "Operations are stable today."
        daily_insight = (
            "No unresolved high-risk issues detected. Continue routine monitoring."
        )
        needs_attention = False

    # --- Top concerns (limit to 3) ---
    top_concerns = unresolved_alerts.order_by("-priority", "-created_at")[:3]

    # --- Simple trend placeholder (honest, not ML) ---
    trend = "normal"
    if total_alerts_today > 5:
        trend = "high"
    elif total_alerts_today > 2:
        trend = "elevated"

    # --- Average daily alerts (last 7 days) ---
    last_week = now() - timedelta(days=7)
    weekly_count = Alert.objects.filter(created_at__gte=last_week).count()
    average_daily = round(weekly_count / 7, 1)
# --- Recommended Actions ---
    recommended_actions = []

    if critical_unresolved > 0:
     recommended_actions.append(
        "Resolve critical alerts immediately to avoid customer loss or revenue impact."
    )

    if medium_alerts.exists():
     recommended_actions.append(
        "Review medium-priority issues and assign staff to prevent escalation."
    )
 
    if not recommended_actions:
     recommended_actions.append(
        "No immediate action required. Continue routine monitoring."
    )

    return {
    "daily_summary": daily_summary,
    "daily_insight": daily_insight,
    "needs_attention": needs_attention,

    "critical_unresolved": critical_unresolved,
    "total_unresolved": total_unresolved,
    "total_alerts_today": total_alerts_today,
    "resolved_today": resolved_today_count,

    "top_concerns": top_concerns,
    "trend": trend,
    "average_daily": average_daily,

    "recommended_actions": recommended_actions,
}
