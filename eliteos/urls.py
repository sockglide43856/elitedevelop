from django.urls import path

from . import views


app_name = "eliteos"


urlpatterns = [

    path(
        "",
        views.eliteos,
        name="eliteos",
    ),

    path(
        "api/filesystem/",
        views.get_filesystem,
        name="get-filesystem",
    ),

    path(
        "api/filesystem/save/",
        views.save_filesystem,
        name="save-filesystem",
    ),

    path(
        "api/filesystem/reset/",
        views.reset_filesystem,
        name="reset-filesystem",
    ),

    path(
        "api/boot/",
        views.record_boot,
        name="record-boot",
    ),

    path(
        "api/system-info/",
        views.system_info,
        name="system-info",
    ),

    path(
        "api/settings/",
        views.settings_api,
        name="settings-api",
    ),

    path(
        "api/store/apps/",
        views.store_apps,
        name="store-apps",
    ),

    path(
        "api/store/submit/",
        views.submit_store_app,
        name="submit-store-app",
    ),

    path(
        "api/store/install/<str:app_id>/",
        views.install_store_app,
        name="install-store-app",
    ),
]