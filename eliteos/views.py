import json
import zlib

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from .models import (
    InstalledApp,
    OSFilesystem,
    OSProfile,
    StoreApp,
)


MAX_COMPRESSED_SIZE = OSFilesystem.MAX_COMPRESSED_SIZE


def default_filesystem(user):

    username = user.username or "User"

    return {
        "/": {
            "type": "directory",
            "name": "/",
        },

        "/home": {
            "type": "directory",
            "name": "home",
        },

        "/home/Desktop": {
            "type": "directory",
            "name": "Desktop",
        },

        "/home/Documents": {
            "type": "directory",
            "name": "Documents",
        },

        "/home/Downloads": {
            "type": "directory",
            "name": "Downloads",
        },

        "/home/Projects": {
            "type": "directory",
            "name": "Projects",
        },

        "/home/Pictures": {
            "type": "directory",
            "name": "Pictures",
        },

        "/home/Music": {
            "type": "directory",
            "name": "Music",
        },

        "/home/Videos": {
            "type": "directory",
            "name": "Videos",
        },

        "/system": {
            "type": "directory",
            "name": "system",
        },

        "/apps": {
            "type": "directory",
            "name": "apps",
        },

        "/home/Documents/Welcome.txt": {
            "type": "file",
            "mime": "text/plain",
            "content": (
                f"Welcome to EliteOS, {username}!\n\n"
                "EliteOS is now ready to use.\n\n"
                "Things you can try:\n"
                "• Browse your virtual filesystem\n"
                "• Write code in Code Studio\n"
                "• Use the EliteOS terminal\n"
                "• Browse websites\n"
                "• Install applications\n"
                "• Customize your desktop\n"
            ),
        },

        "/home/Projects/hello.py": {
            "type": "file",
            "mime": "text/x-python",
            "content": (
                'print("Hello from EliteOS!")\n\n'
                "for number in range(1, 6):\n"
                '    print(f"Counting: {number}")\n'
            ),
        },

        "/home/Projects/index.html": {
            "type": "file",
            "mime": "text/html",
            "content": (
                "<!DOCTYPE html>\n"
                "<html>\n"
                "<head>\n"
                "    <title>Hello EliteOS</title>\n"
                "</head>\n"
                "<body>\n"
                "    <h1>Hello EliteOS!</h1>\n"
                "    <p>This file came from your virtual filesystem.</p>\n"
                "</body>\n"
                "</html>"
            ),
        },

        "/system/about.json": {
            "type": "file",
            "mime": "application/json",
            "content": json.dumps(
                {
                    "name": "EliteOS",
                    "version": "1.0",
                    "codename": "Liquid Glass",
                    "architecture": "Django Web Desktop",
                },
                indent=2,
            ),
        },
    }


def compress_filesystem(filesystem):

    raw = json.dumps(
        filesystem,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    compressed = zlib.compress(
        raw,
        level=9,
    )

    if len(compressed) > MAX_COMPRESSED_SIZE:
        raise ValueError(
            f"Filesystem exceeds the {MAX_COMPRESSED_SIZE} byte limit."
        )

    return compressed


def decompress_filesystem(image):

    if not image:
        return {}

    raw = zlib.decompress(
        bytes(image)
    )

    data = json.loads(
        raw.decode("utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid filesystem."
        )

    return data


def get_or_create_filesystem(user):

    filesystem, created = OSFilesystem.objects.get_or_create(
        user=user
    )

    if created or not filesystem.image:

        data = default_filesystem(user)

        compressed = compress_filesystem(data)

        filesystem.image = compressed
        filesystem.compressed_size = len(compressed)
        filesystem.filesystem_version = 1

        filesystem.save()

    return filesystem


def builtin_apps():

    return [
        {
            "id": "files",
            "name": "Files",
            "description": "Browse and manage your EliteOS filesystem.",
            "icon": "📁",
            "version": "1.0",
            "builtin": True,
        },
        {
            "id": "terminal",
            "name": "Terminal",
            "description": "A shell environment for navigating EliteOS.",
            "icon": "▸_",
            "version": "1.0",
            "builtin": True,
        },
        {
            "id": "code",
            "name": "Code Studio",
            "description": "Create and edit applications and projects.",
            "icon": "⌘",
            "version": "1.0",
            "builtin": True,
        },
        {
            "id": "browser",
            "name": "Elite Browser",
            "description": "Browse the web with tabs and bookmarks.",
            "icon": "🌐",
            "version": "1.0",
            "builtin": True,
        },
        {
            "id": "settings",
            "name": "System Settings",
            "description": "Customize your EliteOS desktop.",
            "icon": "⚙",
            "version": "1.0",
            "builtin": True,
        },
    ]


@login_required
def eliteos(request):

    profile, _ = OSProfile.objects.get_or_create(
        user=request.user
    )

    get_or_create_filesystem(
        request.user
    )

    return render(
        request,
        "eliteos/eliteos.html",
        {
            "eliteos_username": (
                profile.display_name
                or request.user.username
            ),
            "eliteos_user_id": request.user.pk,
        },
    )


@login_required
@require_GET
def get_filesystem(request):

    filesystem = get_or_create_filesystem(
        request.user
    )

    try:
        data = decompress_filesystem(
            filesystem.image
        )

    except Exception as exc:

        return JsonResponse(
            {
                "error": f"Filesystem error: {exc}"
            },
            status=500,
        )

    return JsonResponse(
        {
            "success": True,
            "filesystem": data,
            "compressed_size": filesystem.compressed_size,
            "max_compressed_size": MAX_COMPRESSED_SIZE,
            "version": filesystem.filesystem_version,
        }
    )


@login_required
@require_POST
def save_filesystem(request):

    try:

        payload = json.loads(
            request.body.decode("utf-8")
        )

        data = payload.get(
            "filesystem"
        )

        if not isinstance(data, dict):
            return JsonResponse(
                {
                    "error": "Filesystem must be an object."
                },
                status=400,
            )

        compressed = compress_filesystem(
            data
        )

    except ValueError as exc:

        return JsonResponse(
            {
                "error": str(exc)
            },
            status=413,
        )

    except Exception:

        return JsonResponse(
            {
                "error": "Invalid JSON request."
            },
            status=400,
        )

    filesystem = get_or_create_filesystem(
        request.user
    )

    filesystem.image = compressed
    filesystem.compressed_size = len(compressed)
    filesystem.filesystem_version += 1

    filesystem.save()

    return JsonResponse(
        {
            "success": True,
            "compressed_size": filesystem.compressed_size,
            "max_compressed_size": MAX_COMPRESSED_SIZE,
            "version": filesystem.filesystem_version,
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def reset_filesystem(request):

    data = default_filesystem(
        request.user
    )

    compressed = compress_filesystem(
        data
    )

    filesystem = get_or_create_filesystem(
        request.user
    )

    filesystem.image = compressed
    filesystem.compressed_size = len(compressed)
    filesystem.filesystem_version += 1

    filesystem.save()

    return JsonResponse(
        {
            "success": True,
            "message": "EliteOS filesystem reset successfully.",
            "version": filesystem.filesystem_version,
            "filesystem": data,
        }
    )


@login_required
@require_POST
def record_boot(request):

    profile, _ = OSProfile.objects.get_or_create(
        user=request.user
    )

    profile.boot_count += 1
    profile.last_booted_at = timezone.now()

    profile.save()

    return JsonResponse(
        {
            "success": True,
            "boot_count": profile.boot_count,
        }
    )


@login_required
@require_GET
def system_info(request):

    profile, _ = OSProfile.objects.get_or_create(
        user=request.user
    )

    filesystem = get_or_create_filesystem(
        request.user
    )

    return JsonResponse(
        {
            "username": request.user.username,
            "os": "EliteOS",
            "version": "1.0",
            "codename": "Liquid Glass",
            "boot_count": profile.boot_count,
            "filesystem_version": filesystem.filesystem_version,
            "compressed_size": filesystem.compressed_size,
            "max_compressed_size": MAX_COMPRESSED_SIZE,
            "theme": profile.theme,
            "accent": profile.accent,
            "wallpaper": profile.wallpaper,
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def settings_api(request):

    profile, _ = OSProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "GET":

        return JsonResponse(
            {
                "username": request.user.username,
                "display_name": profile.display_name,
                "wallpaper": profile.wallpaper,
                "accent": profile.accent,
                "theme": profile.theme,
                "panel_position": profile.panel_position,
                "transparency": profile.transparency,
                "animations": profile.animations,
            }
        )

    try:

        payload = json.loads(
            request.body.decode("utf-8")
        )

    except Exception:

        return JsonResponse(
            {
                "error": "Invalid JSON."
            },
            status=400,
        )

    allowed = [
        "display_name",
        "wallpaper",
        "accent",
        "theme",
        "panel_position",
        "transparency",
        "animations",
    ]

    for field in allowed:

        if field in payload:

            value = payload[field]

            if field == "transparency":
                try:
                    value = max(
                        20,
                        min(100, int(value))
                    )
                except Exception:
                    continue

            setattr(
                profile,
                field,
                value,
            )

    profile.save()

    return JsonResponse(
        {
            "success": True
        }
    )


@login_required
@require_GET
def store_apps(request):

    results = builtin_apps()

    installed = set(
        InstalledApp.objects.filter(
            user=request.user
        ).values_list(
            "app_id",
            flat=True,
        )
    )

    for app in results:
        app["installed"] = (
            app["builtin"]
            or app["id"] in installed
        )

    apps = StoreApp.objects.filter(
        status="published"
    ).select_related(
        "author"
    )

    for app in apps:

        results.append(
            {
                "id": app.app_id,
                "name": app.name,
                "description": app.description,
                "icon": app.icon,
                "version": app.version,
                "author": (
                    app.author.username
                    if app.author
                    else "EliteOS Community"
                ),
                "downloads": app.downloads,
                "builtin": False,
                "installed": (
                    app.app_id in installed
                ),
            }
        )

    return JsonResponse(
        {
            "apps": results
        }
    )


@login_required
@require_POST
def submit_store_app(request):

    try:

        payload = json.loads(
            request.body.decode("utf-8")
        )

        app_id = (
            payload.get("app_id")
            or ""
        ).strip().lower()

        name = (
            payload.get("name")
            or ""
        ).strip()

        description = (
            payload.get("description")
            or ""
        ).strip()

        icon = (
            payload.get("icon")
            or "◈"
        )

        version = (
            payload.get("version")
            or "1.0.0"
        )

        source = (
            payload.get("source")
            or {}
        )

        if not app_id or not name:

            return JsonResponse(
                {
                    "error": (
                        "App ID and name are required."
                    )
                },
                status=400,
            )

        if not isinstance(source, dict):

            return JsonResponse(
                {
                    "error": (
                        "App source must be an object."
                    )
                },
                status=400,
            )

        app, created = StoreApp.objects.update_or_create(

            app_id=app_id,

            defaults={
                "author": request.user,
                "name": name,
                "description": description,
                "icon": icon,
                "version": version,
                "source": source,
                "status": "published",
            },
        )

        return JsonResponse(
            {
                "success": True,
                "created": created,
                "message": (
                    "Your app is now available in "
                    "the EliteOS App Store."
                ),
                "app_id": app.app_id,
            }
        )

    except Exception as exc:

        return JsonResponse(
            {
                "error": str(exc)
            },
            status=400,
        )


@login_required
@require_POST
def install_store_app(request, app_id):

    if app_id in {
        app["id"]
        for app in builtin_apps()
    }:

        return JsonResponse(
            {
                "success": True,
                "builtin": True,
                "message": (
                    "This application is built into EliteOS."
                ),
            }
        )

    try:

        app = StoreApp.objects.get(
            app_id=app_id,
            status="published",
        )

    except StoreApp.DoesNotExist:

        return JsonResponse(
            {
                "error": "Application not found."
            },
            status=404,
        )

    InstalledApp.objects.get_or_create(
        user=request.user,
        app_id=app.app_id,
    )

    app.downloads += 1

    app.save(
        update_fields=[
            "downloads"
        ]
    )

    return JsonResponse(
        {
            "success": True,
            "app": {
                "id": app.app_id,
                "name": app.name,
                "source": app.source,
            },
        }
    )