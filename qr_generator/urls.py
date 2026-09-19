from django.urls import path
from .views import generate_qr_view

urlpatterns = [
    path('', generate_qr_view, name='qr-dashboard'),
]