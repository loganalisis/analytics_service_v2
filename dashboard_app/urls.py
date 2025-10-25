from django.urls import path
from .views import get_dashboard, insert_data

urlpatterns = [
    path("dashboard/", get_dashboard),
    path("add/", insert_data),
]
