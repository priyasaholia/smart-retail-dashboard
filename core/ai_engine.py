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

from django.utils.timezone import now
from datetime import timedelta
from collections import Counter, defaultdict

def generate_alert_trends(days=7):
    """
    Phase 3.3.1 — Strengthened Trend & Pattern Intelligence
    Thinks in terms of persistence, severity, and buildup.
    """

    now_time = now()
    since = now_time - timedelta(days=days)

    alerts = Alert.objects.filter(created_at__gte=since)

    if not alerts.exists():
        return {
            "trend_summary": "Not enough historical data to evaluate operational trends.",
            "risk_level": "low",
            "recurring_patterns": [],
        }

    # --- Group alerts by message ---
    message_groups = defaultdict(list)
    for alert in alerts:
        message_groups[alert.message].append(alert)

    recurring_patterns = []
    dominant_risk_score = 0

    for message, group in message_groups.items():
        count = len(group)
        unresolved_count = sum(1 for a in group if not a.resolved)
        critical_count = sum(1 for a in group if a.priority == "critical")

        # Risk scoring (simple but meaningful)
        risk_score = (
            critical_count * 3 +
            unresolved_count * 2 +
            count
        )

        dominant_risk_score += risk_score

        # Only surface meaningful patterns
        if count >= 3 or critical_count >= 2:
            recurring_patterns.append({
                "issue": message,
                "count": count,
                "unresolved": unresolved_count,
                "critical": critical_count,
            })

    # --- Acceleration check (last 2 days vs earlier) ---
    recent_cutoff = now_time - timedelta(days=2)
    recent_count = alerts.filter(created_at__gte=recent_cutoff).count()
    earlier_count = alerts.filter(created_at__lt=recent_cutoff).count()

    accelerating = recent_count > earlier_count

    # --- Risk level reasoning ---
    if dominant_risk_score >= 15 or accelerating:
        risk_level = "high"
        trend_summary = (
            "Operational risks are building up. "
            "Issues are persisting unresolved and appearing more frequently."
        )
    elif dominant_risk_score >= 8:
        risk_level = "elevated"
        trend_summary = (
            "Some issues are repeating and staying unresolved. "
            "If ignored, they may escalate into critical risks."
        )
    else:
        risk_level = "normal"
        trend_summary = (
            "Operational patterns are mostly stable, "
            "with no major risk buildup detected."
        )

    return {
        "trend_summary": trend_summary,
        "risk_level": risk_level,
        "recurring_patterns": recurring_patterns,
    }
