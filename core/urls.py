from django.urls import path
from .views import home, dashboard, ingest_alert, signup, activate
from .views import add_notebook_entry
from .views import view_notebook
from .views import copilot_ask


app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path("dashboard/", dashboard, name="dashboard"),
    path("api/alerts/", ingest_alert, name="ingest_alert"),
    path("notebook/add/", add_notebook_entry, name="add_notebook_entry"),
    path("notebook/", view_notebook, name="view_notebook"),
    path("api/copilot/ask/", copilot_ask, name="copilot_ask"),

]
