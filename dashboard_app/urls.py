from django.urls import path
from .views import get_dashboard, insert_data, get_Log_file

urlpatterns = [
    path("dashboard/", get_dashboard),
    path("add/", insert_data),
    path("get_file/", get_Log_file),
]
