from django.urls import path

from . import views


app_name = "proxy"


urlpatterns = [
    path("", views.index, name="index"),
    path("token/", views.token, name="token"),
    path("authorize-navigation/", views.authorize_navigation, name="authorize_navigation"),
]