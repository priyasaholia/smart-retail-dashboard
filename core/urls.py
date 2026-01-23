from django.urls import path
from .views import home, dashboard, ingest_alert

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("api/alerts/", ingest_alert, name="ingest_alert"),
]
