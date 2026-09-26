from django.urls import path

from . import views


app_name = "collabs"


urlpatterns = [

    path(
        "",
        views.collabs_home,
        name="home",
    ),

    path(
        "create/",
        views.create_collab,
        name="create",
    ),

    path(
        "join/",
        views.join_collab,
        name="join",
    ),

    path(
        "<str:collab_id>/",
        views.collab_detail,
        name="detail",
    ),

    path(
        "<str:collab_id>/files/",
        views.collab_files,
        name="files",
    ),

    path(
        "<str:collab_id>/docs/",
        views.collab_docs,
        name="docs",
    ),

    path(
        "<str:collab_id>/docs/new/",
        views.create_document,
        name="create_document",
    ),

    path(
        "<str:collab_id>/docs/<str:document_id>/",
        views.edit_document,
        name="edit_document",
    ),

    path(
        "<str:collab_id>/links/",
        views.collab_links,
        name="links",
    ),

    path(
        "<str:collab_id>/news/",
        views.collab_news,
        name="news",
    ),

    path(
        "<str:collab_id>/share/",
        views.collab_share,
        name="share",
    ),

    path(
        "<str:collab_id>/chats/",
        views.collab_chats,
        name="chats",
    ),
]