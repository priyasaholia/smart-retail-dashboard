from django.urls import path
from .views import home, dashboard
from .views import create_alert_api


urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("api/alerts/", create_alert_api),
]
