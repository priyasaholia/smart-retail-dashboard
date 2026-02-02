from datetime import date
from .models import Alert
from .models import NotebookEntry
def build_alert_evidence(alert):
    return {
        "id": alert.id,
        "message": alert.message,
        "priority": alert.priority,
        "source": alert.source,
        "created_at": alert.created_at,
        "url": f"/dashboard/?focus=alert:{alert.id}"
    }


def build_notebook_evidence(entry):
    return {
        "id": entry.id,
        "type": entry.entry_type,
        "amount": entry.amount,
        "description": entry.description,
        "created_at": entry.created_at,
        "url": f"/notebook/?focus=entry:{entry.id}"
    }


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
from django.db.models import Avg, Min, Max
from django.utils.timezone import now
from datetime import timedelta

def generate_financial_baseline(days=14):
    """
    Phase 4.3 — Financial Baseline Computation
    Learns what 'normal' looks like from notebook data.
    """

    since = now() - timedelta(days=days)

    entries = NotebookEntry.objects.filter(
        created_at__gte=since,
        amount__isnull=False
    )

    if not entries.exists():
        return {
            "baseline_summary": "Not enough financial data to establish a baseline yet.",
            "baseline": {}
        }

    baseline = {}

    for entry_type in ["expense", "sale", "purchase"]:
        subset = entries.filter(entry_type=entry_type)

        if subset.exists():
            baseline[entry_type] = {
                "average": round(subset.aggregate(Avg("amount"))["amount__avg"], 2),
                "min": round(subset.aggregate(Min("amount"))["amount__min"], 2),
                "max": round(subset.aggregate(Max("amount"))["amount__max"], 2),
                "count": subset.count(),
            }

    baseline_summary = (
        "Financial baseline established using recent notebook activity. "
        "The system now understands normal spending and sales patterns."
    )

    return {
        "baseline_summary": baseline_summary,
        "baseline": baseline
    }
def detect_financial_anomaly(entry):
    """
    Phase 4.4 — Financial Anomaly Detection
    Compares a notebook entry against learned baseline
    """

    baseline_data = generate_financial_baseline()

    baseline = baseline_data.get("baseline", {})
    entry_type = entry.entry_type
    amount = entry.amount

    if not baseline or entry_type not in baseline:
        return None  # Not enough context to judge

    avg = baseline[entry_type]["average"]

    # Define thresholds
    if entry_type in ["expense", "purchase"]:
        if amount > 1.5 * avg:
            return {
                "type": "high_expense",
                "message": (
                    f"{entry_type.capitalize()} of ₹{amount} is significantly "
                    f"higher than the normal average of ₹{avg}."
                ),
                "priority": "medium"
            }

    if entry_type == "sale":
        if amount < 0.6 * avg:
            return {
                "type": "low_sale",
                "message": (
                    f"Sale of ₹{amount} is significantly lower than the "
                    f"normal average of ₹{avg}."
                ),
                "priority": "medium"
            }

    return None
def generate_financial_alert(entry):
    """
    Converts financial anomalies into system alerts
    """

    anomaly = detect_financial_anomaly(entry)

    if not anomaly:
        return None

    priority, explanation = generate_alert_intelligence(anomaly["message"])

    alert = Alert.objects.create(
        message=anomaly["message"],
        source="financial_notebook",
        priority=priority,
        ai_explanation=explanation
    )

    return alert
def generate_financial_trends(days=14):
    """
    Phase 4.5 — Financial Trend Intelligence
    Detects persistent financial risk patterns over time.
    """

    baseline_data = generate_financial_baseline(days=days)
    baseline = baseline_data.get("baseline", {})

    if not baseline:
        return {
            "financial_trend_summary": "Not enough financial data to detect trends yet.",
            "financial_risk_level": "low",
        }

    from django.utils.timezone import now
    from datetime import timedelta

    recent_since = now() - timedelta(days=3)
    recent_entries = NotebookEntry.objects.filter(
        created_at__gte=recent_since,
        amount__isnull=False,
        entry_type="expense"
    )

    if not recent_entries.exists():
        return {
            "financial_trend_summary": "No recent financial anomalies detected.",
            "financial_risk_level": "normal",
        }

    recent_avg = recent_entries.aggregate(Avg("amount"))["amount__avg"]
    baseline_avg = baseline.get("expense", {}).get("average")

    if not baseline_avg:
        return {
            "financial_trend_summary": "Insufficient baseline for expense trends.",
            "financial_risk_level": "low",
        }

    # Persistent overspending detection
    if recent_avg > 1.3 * baseline_avg:
        return {
            "financial_trend_summary": (
                "Expenses have been consistently higher than normal in recent days. "
                "This suggests ongoing overspending rather than a one-time anomaly."
            ),
            "financial_risk_level": "elevated",
        }

    return {
        "financial_trend_summary": "Expense patterns remain within expected ranges.",
        "financial_risk_level": "normal",
    }
def generate_financial_trend_alert():
    """
    Converts financial trend risks into system alerts.
    """

    trend = generate_financial_trends()

    if trend["financial_risk_level"] != "elevated":
        return None

    priority, explanation = generate_alert_intelligence(
        trend["financial_trend_summary"]
    )

    alert = Alert.objects.create(
        message=trend["financial_trend_summary"],
        source="financial_trends",
        priority=priority,
        ai_explanation=explanation
    )

    return alert
# =========================================================
# PHASE 6 — CONTEXTUAL AI Q&A (COPILOT CORE)
# =========================================================

def classify_question_intent(question):
    """
    Phase 6.1 — Classify Copilot question intent
    """
    q = question.lower()

    if "today" in q or "attention" in q or "now" in q:
        return "daily_status"

    if "expense" in q or "money" in q or "spending" in q:
        return "financial_reasoning"

    if "trend" in q or "recurring" in q or "pattern" in q:
        return "trend_reasoning"

    if "why" in q and "alert" in q:
        return "system_explanation"

    return "unknown"


def assemble_context_for_question(intent):
    """
    Phase 6.2 — Assemble system context for Copilot
    """
    context = {}

    if intent == "daily_status":
        context["daily"] = generate_daily_intelligence()

    elif intent == "financial_reasoning":
        context["financial_trends"] = generate_financial_trends()

    elif intent == "trend_reasoning":
        context["alert_trends"] = generate_alert_trends()

    elif intent == "system_explanation":
        context["system"] = {
            "alert_logic": "Alerts are prioritized based on customer impact, urgency, and risk.",
            "trend_logic": "Trends detect persistence, repetition, and escalation over time.",
        }

    return context


def generate_copilot_answer(question):
    """
    Evidence-driven, state-aware Copilot reasoning
    """

    intent = classify_question_intent(question)
    state = get_system_state_snapshot()
    def respond(answer_text, confidence="MEDIUM"):
     return {
        "answer": answer_text,
        "evidence": state,
        "confidence": confidence,
    }

    alerts = state["alerts"]
    financial = state["financial"]
    trends = state["trends"]

    # ---------------- DAILY STATUS ----------------
    if intent == "daily_status":
        parts = []

        if alerts["critical_unresolved"] > 0:
            parts.append(
                f"There are {alerts['critical_unresolved']} unresolved critical alerts."
            )

        if alerts["recent_24h"] > 0:
            parts.append(
                f"{alerts['recent_24h']} alerts were generated in the last 24 hours."
            )

        if alerts["recent_examples"]:
            parts.append(
                f"Recent issues include: {', '.join(alerts['recent_examples'])}."
            )

        if financial["risk_level"] == "elevated":
            parts.append("Financial risk is elevated due to sustained overspending.")

        if not parts:
         return respond(
        "Operations are stable today. No critical alerts or financial risks "
        "are currently detected.",
        confidence="HIGH",
    )


        return respond(
    "Today is considered risky because "
    + " ".join(parts)
    + " Recommended action: resolve critical alerts first and review finances.",
    confidence="HIGH",
)


    # ---------------- FINANCIAL REASONING ----------------
    if intent == "financial_reasoning":
       return respond(
    f"Financial analysis shows a risk level of '{financial['risk_level']}'. "
    f"{financial['summary']} "
    "This conclusion is based on recent notebook entries compared against "
    "learned spending baselines.",
    confidence="MEDIUM",
)


    # ---------------- TREND REASONING ----------------
    if intent == "trend_reasoning":
        return respond(
    f"Trend analysis indicates a '{trends['risk_level']}' operational risk. "
    f"{trends['summary']} "
    "Recurring unresolved issues suggest systemic problems rather than isolated events.",
    confidence="HIGH",
)


    # ---------------- SYSTEM EXPLANATION ----------------
    if intent == "system_explanation":
        return respond(
    "This system reasons over live operational, financial, and trend data. "
    "It prioritizes issues based on customer impact, urgency, recurrence, "
    "and financial deviation from normal behavior.",
    confidence="HIGH",
)


    # ---------------- FALLBACK ----------------
    return respond(
    "I couldn't fully understand that question. "
    "Try asking about today's risks, expenses, or recurring issues.",
    confidence="LOW",
)

def get_system_state_snapshot():
    """
    Live snapshot of system state for Copilot reasoning
    """

    from django.utils.timezone import now
    from datetime import timedelta

    unresolved = Alert.objects.filter(resolved=False)
    critical = unresolved.filter(priority="critical")
    medium = unresolved.filter(priority="medium")

    last_24h = now() - timedelta(hours=24)
    recent_alerts = unresolved.filter(created_at__gte=last_24h)
    recent_alert_objects = recent_alerts[:5]

    financial_trends = generate_financial_trends()
    alert_trends = generate_alert_trends()

    return {
        "alerts": {
    "total_unresolved": unresolved.count(),
    "critical_unresolved": critical.count(),
    "medium_unresolved": medium.count(),
    "recent_24h": recent_alerts.count(),
    "recent_examples": list(
        recent_alerts.values_list("message", flat=True)[:2]
    ),
    "recent_alert_evidence": [
        build_alert_evidence(a) for a in recent_alert_objects
    ],
},

        "financial": {
            "risk_level": financial_trends.get("financial_risk_level"),
            "summary": financial_trends.get("financial_trend_summary"),
        },
        "trends": {
            "risk_level": alert_trends.get("risk_level"),
            "summary": alert_trends.get("trend_summary"),
        },
        "timestamp": now().strftime("%Y-%m-%d %H:%M"),
    }
def generate_notebook_observations():
    """
    Phase T-1A — Notebook Intelligence Feedback
    Produces human-readable observations from notebook data
    Returns structured dictionary with 5 insight types
    """

    observations = {
        "primary_insight": None,
        "spending_pattern": None,
        "category_insight": None,
        "anomaly_insight": None,
        "recommendation": None,
    }

    # Use existing intelligence
    baseline_data = generate_financial_baseline()
    financial_trends = generate_financial_trends()

    baseline = baseline_data.get("baseline", {})
    entries = NotebookEntry.objects.all().order_by("-created_at")[:20]

    if not entries.exists():
        return observations

    # 1. PRIMARY_INSIGHT: Expense-to-sales ratio analysis
    if "expense" in baseline and "sale" in baseline:
        exp_avg = baseline["expense"]["average"]
        sale_avg = baseline["sale"]["average"]
        if exp_avg > 0 and sale_avg > 0:
            ratio = (exp_avg / sale_avg) * 100
            if exp_avg > sale_avg:
                observations["primary_insight"] = (
                    f"Your expenses average ₹{exp_avg:.0f} vs sales of ₹{sale_avg:.0f}, "
                    f"creating a {ratio:.0f}% expense-to-sales ratio that warrants attention."
                )
            else:
                observations["primary_insight"] = (
                    f"Sales averaging ₹{sale_avg:.0f} outpace expenses of ₹{exp_avg:.0f}, "
                    f"which is a healthy financial position."
                )

    # 2. SPENDING_PATTERN: Trend-based commentary
    if financial_trends.get("financial_risk_level") in ["elevated", "high"]:
        observations["spending_pattern"] = (
            "Recent spending shows an upward trend compared to your learned baseline, "
            "indicating potential budget pressure or changing business patterns."
        )
    elif financial_trends.get("financial_risk_level") == "low":
        observations["spending_pattern"] = (
            "Your spending pattern is stable and within established norms. "
            "Consistency suggests predictable financial behavior."
        )

    # 3. CATEGORY_INSIGHT: Most common entry type percentage
    from collections import Counter
    if entries.exists():
        types = Counter(e.entry_type for e in entries)
        dominant, count = types.most_common(1)[0]
        percentage = (count / len(entries)) * 100

        observations["category_insight"] = (
            f"'{dominant}' entries comprise {percentage:.0f}% of recent activity, "
            f"making them the primary driver of your financial narrative."
        )

    # 4. ANOMALY_INSIGHT: Large transaction detection
    recent_entries_list = list(entries)
    if recent_entries_list:
        amounts = [e.amount for e in recent_entries_list if e.amount]
        if len(amounts) >= 3:
            avg_amount = sum(amounts) / len(amounts)
            std_dev = (sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
            
            for entry in recent_entries_list[:5]:
                if entry.amount and entry.amount > (avg_amount + 2 * std_dev):
                    observations["anomaly_insight"] = (
                        f"A {entry.entry_type} entry of ₹{entry.amount:.0f} stands out "
                        f"as significantly larger than your typical ₹{avg_amount:.0f} transaction."
                    )
                    break

    # 5. RECOMMENDATION: Action-based guidance
    if observations["primary_insight"] and "expense" in baseline and "sale" in baseline:
        if baseline["expense"]["average"] > baseline["sale"]["average"]:
            observations["recommendation"] = (
                "Consider reviewing your largest expense categories to identify "
                "cost optimization opportunities."
            )
        else:
            observations["recommendation"] = (
                "Your financial trajectory is positive. Focus on maintaining "
                "current spending discipline while exploring growth opportunities."
            )

    return observations


def get_entry_intelligence_markers():
    """
    Phase T-1B — Entry-Level Intelligence Markers
    Derives subtle visual markers for individual entries based on existing intelligence.
    
    Returns dict: {entry_id: {"anomaly": bool, "trend_contributor": bool, "category_pattern": bool}}
    
    Markers are derived from:
    - Anomaly detection: Entry amount deviates 2+ std dev from baseline
    - Trend contribution: Entry is in recent high-spending period (elevated risk level)
    - Category pattern: Entry type is dominant in recent activity
    
    This makes the notebook act as explainable evidence for system reasoning.
    """
    
    from django.db.models import Avg
    from collections import Counter
    
    markers = {}
    
    # Get all notebook entries
    entries = NotebookEntry.objects.all().order_by("-created_at")
    if not entries.exists():
        return markers
    
    # Get baseline for anomaly detection
    baseline_data = generate_financial_baseline()
    baseline = baseline_data.get("baseline", {})
    
    # Get trend data for contribution detection
    financial_trends = generate_financial_trends()
    is_elevated_spending = financial_trends.get("financial_risk_level") in ["elevated", "high"]
    
    # Get recent entries for trend and category detection
    recent_since = now() - timedelta(days=3)
    recent_entries = NotebookEntry.objects.filter(created_at__gte=recent_since)
    
    # Compute category dominance
    recent_types = Counter(e.entry_type for e in recent_entries)
    dominant_type = recent_types.most_common(1)[0][0] if recent_types else None
    
    # Compute anomaly thresholds for recent entries
    recent_with_amounts = recent_entries.filter(amount__isnull=False)
    if recent_with_amounts.exists():
        amounts = [e.amount for e in recent_with_amounts]
        avg_recent = sum(amounts) / len(amounts)
        std_dev = (sum((x - avg_recent) ** 2 for x in amounts) / len(amounts)) ** 0.5
        anomaly_threshold = avg_recent + (2 * std_dev) if std_dev > 0 else float('inf')
    else:
        anomaly_threshold = float('inf')
    
    # Process each entry
    for entry in entries:
        entry_markers = {
            "anomaly": False,
            "trend_contributor": False,
            "category_pattern": False,
        }
        
        # 1. ANOMALY: Check against baseline
        if baseline and entry.entry_type in baseline and entry.amount:
            entry_avg = baseline[entry.entry_type]["average"]
            # Anomaly if 1.5x the baseline average (high expense/purchase or low sale)
            if entry.entry_type in ["expense", "purchase"]:
                if entry.amount > 1.5 * entry_avg:
                    entry_markers["anomaly"] = True
            elif entry.entry_type == "sale":
                if entry.amount < 0.6 * entry_avg:
                    entry_markers["anomaly"] = True
        
        # 2. TREND_CONTRIBUTOR: Is this entry in a recent elevated spending period?
        if is_elevated_spending and entry.entry_type in ["expense", "purchase"]:
            if entry.created_at >= recent_since and entry.amount:
                entry_markers["trend_contributor"] = True
        
        # 3. CATEGORY_PATTERN: Is this entry type the dominant category?
        if entry.entry_type == dominant_type:
            entry_markers["category_pattern"] = True
        
        markers[entry.id] = entry_markers
    
    return markers

