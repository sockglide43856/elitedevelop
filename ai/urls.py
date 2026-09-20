from django.urls import path

from . import views

app_name = "ai"

urlpatterns = [
    path("", views.rooms, name="rooms"),
    path("room/<int:room_id>/", views.room, name="room"),

    path(
        "room/create/",
        views.create_room,
        name="create_room",
    ),

    path(
        "room/<int:room_id>/delete/",
        views.delete_room,
        name="delete_room",
    ),

    path(
        "room/<int:room_id>/message/",
        views.send_message,
        name="send_message",
    ),
    path(
        "job/<str:job_id>/",
        views.job_status,
        name="job_status",
)   ,
]