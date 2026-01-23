from django.urls import path
from .views import home, dashboard, ingest_alert
from .views import add_notebook_entry


app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("api/alerts/", ingest_alert, name="ingest_alert"),
    path("notebook/add/", add_notebook_entry, name="add_notebook_entry"),
    
]
