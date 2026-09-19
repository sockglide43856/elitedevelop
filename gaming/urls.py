from django.urls import path
from . import views

urlpatterns = [
    path('', views.gaming_home, name='gaming_home'),
    path('arcade/', views.arcade_coin_flip, name='arcade'),
    path('transfer/', views.transfer_electis, name='transfer'),
]