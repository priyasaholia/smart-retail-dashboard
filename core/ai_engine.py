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
