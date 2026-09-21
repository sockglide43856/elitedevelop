from django.urls import path

from . import views


app_name = "ai"


urlpatterns = [
    path(
        "",
        views.rooms,
        name="rooms",
    ),

    path(
        "room/<int:room_id>/",
        views.room,
        name="room",
    ),

    path(
        "room/create/",
        views.create_room,
        name="create_room",
    ),

    path(
        "room/<int:room_id>/rename/",
        views.rename_room,
        name="rename_room",
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
        "room/<int:room_id>/memory/create/",
        views.create_room_memory,
        name="create_room_memory",
    ),

    path(
        "memory/<int:memory_id>/delete/",
        views.delete_room_memory,
        name="delete_room_memory",
    ),

    path(
        "job/<str:job_id>/complete/",
        views.complete_job,
        name="complete_job",
    ),

    path(
        "settings/",
        views.settings_view,
        name="settings",
    ),

    path(
        "settings/update/",
        views.update_settings,
        name="update_settings",
    ),

    path(
        "settings/memory/create/",
        views.create_user_memory,
        name="create_user_memory",
    ),

    path(
        "settings/memory/<int:memory_id>/delete/",
        views.delete_user_memory,
        name="delete_user_memory",
    ),

    # Global page-aware Apex
    path(
        "context/",
        views.page_context,
        name="page_context",
    ),
]