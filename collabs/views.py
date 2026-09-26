from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import base64
import io
import mimetypes
import os
import posixpath
import zipfile
from django.http import HttpResponse
from . import cloudflare
from chat.models import (
    PrivateChatMembership,
    PrivateMessage,
)



User = get_user_model()

@login_required
def share_file(request, collab_id, file_id):
    try:
        file = cloudflare.get_file(
            file_id
        )["file"]

    except Exception as e:
        messages.error(
            request,
            f"Could not load file: {e}",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    memberships = (
        PrivateChatMembership.objects
        .filter(user=request.user)
        .select_related("room")
        .order_by("room__name")
    )

    if request.method == "POST":

        membership_id = request.POST.get(
            "membership_id"
        )

        membership = (
            memberships
            .filter(id=membership_id)
            .first()
        )

        if not membership:
            messages.error(
                request,
                "That private chat could not be found.",
            )

            return redirect(
                "collabs:share_file",
                collab_id=collab_id,
                file_id=file_id,
            )

        share_url = request.build_absolute_uri(
            f"/collabs/{collab_id}/files/"
            f"{file_id}/download/"
        )

        message_text = (
            f'📎 Shared file: {file["name"]}\n'
            f'{share_url}'
        )

        PrivateMessage.objects.create(
            room=membership.room,
            author=request.user,
            message=message_text,
        )

        messages.success(
            request,
            f'Shared "{file["name"]}" in '
            f'{membership.room.name}.',
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    return render(
        request,
        "collabs/share_file.html",
        {
            "collab": cloudflare.get_collab(
                collab_id
            )["collab"],
            "file": file,
            "memberships": memberships,
        },
    )

@login_required
def collabs_home(request):
    try:
        collabs = cloudflare.list_collabs(
            request.user.id
        ).get("collabs", [])
    except Exception as e:
        collabs = []
        messages.error(request, f"Could not load Collabs: {e}")

    return render(
        request,
        "collabs/home.html",
        {"collabs": collabs},
    )


@login_required
def create_collab(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Collab name is required.")
        else:
            try:
                result = cloudflare.create_collab(
                    name,
                    description,
                    request.user.id,
                )

                collab = result["collab"]

                messages.success(
                    request,
                    "Collab created successfully.",
                )

                return redirect(
                    "collabs:detail",
                    collab_id=collab["id"],
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Could not create Collab: {e}",
                )

    return render(request, "collabs/create.html")


@login_required
def collab_detail(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        pins = cloudflare.list_pins(
            collab_id
        ).get("pins", [])

        activity = cloudflare.list_activity(
            collab_id
        ).get("activity", [])

        # Resolve activity user IDs to actual usernames.
        user_ids = {
            event.get("user_id")
            for event in activity
            if event.get("user_id") is not None
        }

        users = User.objects.in_bulk(user_ids)

        for event in activity:
            user = users.get(event.get("user_id"))

            if user:
                event["username"] = user.username
            else:
                event["username"] = "Unknown user"

    except Exception as e:
        messages.error(
            request,
            f"Could not load Collab: {e}",
        )

        return redirect("collabs:home")

    return render(
        request,
        "collabs/detail.html",
        {
            "collab": collab,
            "pins": pins,
            "activity": activity,
        },
    )

@login_required
def collab_docs(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        documents = cloudflare.list_documents(
            collab_id
        ).get("documents", [])

    except Exception as e:
        messages.error(
            request,
            f"Could not load documents: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    return render(
        request,
        "collabs/docs.html",
        {
            "collab": collab,
            "documents": documents,
        },
    )


@login_required
def create_document(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]
    except Exception as e:
        messages.error(
            request,
            f"Could not load Collab: {e}",
        )

        return redirect("collabs:home")

    if request.method == "POST":
        title = request.POST.get(
            "title",
            "",
        ).strip()

        content = request.POST.get(
            "content",
            "",
        )

        if not title:
            messages.error(
                request,
                "Document title is required.",
            )

            return render(
                request,
                "collabs/create_document.html",
                {"collab": collab},
            )

        try:
            result = cloudflare.create_document(
                collab_id,
                title,
                content,
                request.user.id,
            )

            document = result["document"]

            return redirect(
                "collabs:edit_document",
                collab_id=collab_id,
                document_id=document["id"],
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not create document: {e}",
            )

    return render(
        request,
        "collabs/create_document.html",
        {"collab": collab},
    )


@login_required
def edit_document(request, collab_id, document_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        document = cloudflare.get_document(
            document_id
        )["document"]

    except Exception as e:
        messages.error(
            request,
            f"Could not load document: {e}",
        )

        return redirect(
            "collabs:docs",
            collab_id=collab_id,
        )

    if request.method == "POST":
        try:
            document = cloudflare.update_document(
                document_id,
                request.POST.get(
                    "title",
                    document["title"],
                ),
                request.POST.get(
                    "content",
                    document["content"],
                ),
                request.user.id,
            )["document"]

            messages.success(
                request,
                "Document saved.",
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not save document: {e}",
            )

    return render(
        request,
        "collabs/edit_document.html",
        {
            "collab": collab,
            "document": document,
        },
    )


@login_required
def collab_files(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        files = cloudflare.list_files(
            collab_id
        ).get("files", [])

    except Exception as e:
        messages.error(
            request,
            f"Could not load files: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    current_folder = request.GET.get("folder") or None

    file_map = {
        file["id"]: file
        for file in files
    }

    visible_files = []

    for file in files:
        if file.get("parent_id") == current_folder:
            visible_files.append(file)

    breadcrumbs = []

    folder = file_map.get(current_folder)

    while folder:
        breadcrumbs.insert(
            0,
            folder,
        )

        folder = file_map.get(
            folder.get("parent_id")
        )

    return render(
        request,
        "collabs/files.html",
        {
            "collab": collab,
            "files": visible_files,
            "all_files": files,
            "current_folder": current_folder,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def open_file(request, collab_id, file_id):
    try:
        result = cloudflare.get_file(
            file_id
        )

        file = result["file"]

    except Exception as e:
        messages.error(
            request,
            f"Could not open file: {e}",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    if file.get("is_directory"):
        return redirect(
            f"{request.path.rsplit('/', 2)[0]}/?folder={file_id}"
        )

    encoded = file.get("data")

    if not encoded:
        messages.error(
            request,
            "This file has no stored data.",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    try:
        data = base64.b64decode(encoded)
    except Exception:
        messages.error(
            request,
            "The stored file data is invalid.",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    mime_type = (
        file.get("mime_type")
        or "application/octet-stream"
    )

    # HTML gets rendered through a sandboxed preview.
    if mime_type in {
        "text/html",
        "application/xhtml+xml",
    }:
        return render(
            request,
            "collabs/file_preview.html",
            {
                "collab": {
                    "id": collab_id,
                    "name": "",
                },
                "file": file,
                "content": data.decode(
                    "utf-8",
                    errors="replace",
                ),
            },
        )

    response = HttpResponse(
        data,
        content_type=mime_type,
    )

    response[
        "Content-Disposition"
    ] = f'inline; filename="{file["name"]}"'

    return response


@login_required
def download_file(request, collab_id, file_id):
    try:
        file = cloudflare.get_file(
            file_id
        )["file"]

    except Exception as e:
        messages.error(
            request,
            f"Could not download file: {e}",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    if file.get("is_directory"):
        messages.error(
            request,
            "Folders cannot be downloaded directly.",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    encoded = file.get("data")

    if not encoded:
        messages.error(
            request,
            "This file has no stored data.",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    try:
        data = base64.b64decode(encoded)
    except Exception:
        messages.error(
            request,
            "The stored file data is invalid.",
        )

        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    response = HttpResponse(
        data,
        content_type=(
            file.get("mime_type")
            or "application/octet-stream"
        ),
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{file["name"]}"'

    return response

@login_required
def file_action(request, collab_id):
    if request.method != "POST":
        return redirect(
            "collabs:files",
            collab_id=collab_id,
        )

    action = request.POST.get("action")

    file_id = request.POST.get(
        "file_id"
    )

    current_folder = request.POST.get(
        "current_folder"
    ) or None

    # -------------------------
    # RENAME
    # -------------------------

    if action == "rename":
        name = request.POST.get(
            "name",
            "",
        ).strip()

        if not file_id or not name:
            messages.error(
                request,
                "A file name is required.",
            )

        else:
            try:
                cloudflare.update_file(
                    file_id,
                    request.user.id,
                    name=name,
                )

                messages.success(
                    request,
                    "Renamed successfully.",
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Could not rename: {e}",
                )

    # -------------------------
    # DELETE
    # -------------------------

    elif action == "delete":
        if not file_id:
            messages.error(
                request,
                "No file selected.",
            )

        else:
            try:
                cloudflare.delete_file(
                    file_id,
                    request.user.id,
                )

                messages.success(
                    request,
                    "Deleted successfully.",
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Could not delete: {e}",
                )

    # -------------------------
    # MOVE
    # -------------------------

    elif action == "move":
        parent_id = request.POST.get(
            "parent_id"
        ) or None

        try:
            cloudflare.update_file(
                file_id,
                request.user.id,
                parent_id=parent_id,
            )

            messages.success(
                request,
                "Moved successfully.",
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not move: {e}",
            )

    # -------------------------
    # COPY
    # -------------------------

    elif action == "copy":
        try:
            source = cloudflare.get_file(
                file_id
            )["file"]

            encoded_data = source.get(
                "data"
            )

            cloudflare.create_file(
                collab_id=collab_id,
                name=source["name"],
                mime_type=source.get(
                    "mime_type",
                    "application/octet-stream",
                ),
                size=source.get(
                    "size",
                    0,
                ),
                created_by=request.user.id,
                data=encoded_data,
                parent_id=current_folder,
                is_directory=bool(
                    source.get("is_directory")
                ),
            )

            messages.success(
                request,
                "Copied successfully.",
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not copy: {e}",
            )

    # -------------------------
    # COMPRESS
    # -------------------------

    elif action == "compress":
        try:
            source = cloudflare.get_file(
                file_id
            )["file"]

            if source.get("is_directory"):
                raise RuntimeError(
                    "Folder compression requires its child files to be loaded."
                )

            encoded_data = source.get(
                "data"
            )

            if not encoded_data:
                raise RuntimeError(
                    "The selected file has no data."
                )

            raw = base64.b64decode(
                encoded_data
            )

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer,
                "w",
                zipfile.ZIP_DEFLATED,
            ) as archive:
                archive.writestr(
                    source["name"],
                    raw,
                )

            zip_data = zip_buffer.getvalue()

            encoded_zip = base64.b64encode(
                zip_data
            ).decode("ascii")

            cloudflare.create_file(
                collab_id=collab_id,
                name=f'{source["name"]}.zip',
                mime_type="application/zip",
                size=len(zip_data),
                created_by=request.user.id,
                data=encoded_zip,
                parent_id=current_folder,
                is_directory=False,
            )

            messages.success(
                request,
                "ZIP created successfully.",
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not compress: {e}",
            )

    # -------------------------
    # EXTRACT
    # -------------------------

    elif action == "extract":
        try:
            source = cloudflare.get_file(
                file_id
            )["file"]

            encoded_data = source.get(
                "data"
            )

            if not encoded_data:
                raise RuntimeError(
                    "The ZIP has no stored data."
                )

            raw = base64.b64decode(
                encoded_data
            )

            with zipfile.ZipFile(
                io.BytesIO(raw)
            ) as archive:

                folder_cache = {
                    "": current_folder
                }

                for member in archive.infolist():

                    safe_name = posixpath.normpath(
                        member.filename
                    )

                    if (
                        safe_name.startswith("../")
                        or safe_name.startswith("/")
                    ):
                        continue

                    parts = [
                        part
                        for part in safe_name.split("/")
                        if part
                    ]

                    if not parts:
                        continue

                    parent_id = current_folder

                    for directory_name in parts[:-1]:

                        cache_key = posixpath.join(
                            *parts[
                                :parts.index(
                                    directory_name
                                ) + 1
                            ]
                        )

                        if cache_key in folder_cache:
                            parent_id = folder_cache[
                                cache_key
                            ]
                            continue

                        result = cloudflare.create_file(
                            collab_id=collab_id,
                            name=directory_name,
                            mime_type="inode/directory",
                            size=0,
                            created_by=request.user.id,
                            parent_id=parent_id,
                            is_directory=True,
                        )

                        folder_id = result[
                            "file"
                        ]["id"]

                        folder_cache[
                            cache_key
                        ] = folder_id

                        parent_id = folder_id

                    filename = parts[-1]

                    if member.is_dir():
                        result = cloudflare.create_file(
                            collab_id=collab_id,
                            name=filename,
                            mime_type="inode/directory",
                            size=0,
                            created_by=request.user.id,
                            parent_id=parent_id,
                            is_directory=True,
                        )

                    else:
                        file_data = archive.read(
                            member
                        )

                        encoded = base64.b64encode(
                            file_data
                        ).decode("ascii")

                        mime_type = (
                            mimetypes.guess_type(
                                filename
                            )[0]
                            or "application/octet-stream"
                        )

                        cloudflare.create_file(
                            collab_id=collab_id,
                            name=filename,
                            mime_type=mime_type,
                            size=len(file_data),
                            created_by=request.user.id,
                            data=encoded,
                            parent_id=parent_id,
                            is_directory=False,
                        )

            messages.success(
                request,
                "ZIP extracted successfully.",
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not extract ZIP: {e}",
            )

    return redirect(
        f"/collabs/{collab_id}/files/"
        + (
            f"?folder={current_folder}"
            if current_folder
            else ""
        )
    )

@login_required
def collab_links(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        links = cloudflare.list_links(
            collab_id
        ).get("links", [])

    except Exception as e:
        messages.error(
            request,
            f"Could not load links: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    if request.method == "POST":
        title = request.POST.get(
            "title",
            "",
        ).strip()

        url = request.POST.get(
            "url",
            "",
        ).strip()

        if not title:
            messages.error(
                request,
                "Link title is required.",
            )

        elif not url:
            messages.error(
                request,
                "URL is required.",
            )

        else:
            try:
                cloudflare.create_link(
                    collab_id=collab_id,
                    title=title,
                    url=url,
                    created_by=request.user.id,
                )

                messages.success(
                    request,
                    "Link added.",
                )

                return redirect(
                    "collabs:links",
                    collab_id=collab_id,
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Could not add link: {e}",
                )

    return render(
        request,
        "collabs/links.html",
        {
            "collab": collab,
            "links": links,
        },
    )


@login_required
def collab_news(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        activity = cloudflare.list_activity(
            collab_id
        ).get("activity", [])

    except Exception as e:
        messages.error(
            request,
            f"Could not load Collab news: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    return render(
        request,
        "collabs/news.html",
        {
            "collab": collab,
            "activity": activity,
        },
    )


@login_required
def collab_share(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        members = cloudflare.list_members(
            collab_id
        ).get("members", [])

        invites = cloudflare.list_invites(
            collab_id
        ).get("invites", [])

        # Resolve member IDs to actual Django usernames.
        user_ids = {
            member.get("user_id")
            for member in members
            if member.get("user_id") is not None
        }

        users = User.objects.in_bulk(user_ids)

        for member in members:
            user = users.get(member.get("user_id"))

            if user:
                member["username"] = user.username
                member["first_name"] = user.first_name.strip() or ""
                member["display_name"] = (
                    user.get_full_name().strip()
                    or user.username
                )
            else:
                member["username"] = "Unknown user"
                member["first_name"] = ""
                member["display_name"] = "Unknown user"

    except Exception as e:
        messages.error(
            request,
            f"Could not load sharing: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    if request.method == "POST":
        role = request.POST.get(
            "role",
            "viewer",
        )

        if role not in {
            "viewer",
            "contributor",
            "editor",
        }:
            role = "viewer"

        try:
            cloudflare.create_invite(
                collab_id,
                request.user.id,
                role,
            )

            messages.success(
                request,
                "Invite created.",
            )

            return redirect(
                "collabs:share",
                collab_id=collab_id,
            )

        except Exception as e:
            messages.error(
                request,
                f"Could not create invite: {e}",
            )

    return render(
        request,
        "collabs/share.html",
        {
            "collab": collab,
            "members": members,
            "invites": invites,
        },
    )

@login_required
def join_collab(request):
    if request.method == "POST":
        code = request.POST.get(
            "code",
            "",
        ).strip().upper()

        if not code:
            messages.error(
                request,
                "Invite code is required.",
            )

        else:
            try:
                result = cloudflare.join_invite(
                    code,
                    request.user.id,
                )

                collab = result["collab"]

                messages.success(
                    request,
                    f"You joined {collab['name']}.",
                )

                return redirect(
                    "collabs:detail",
                    collab_id=collab["id"],
                )

            except Exception as e:
                messages.error(
                    request,
                    f"Could not join Collab: {e}",
                )

    return render(
        request,
        "collabs/join.html",
    )


@login_required
def collab_chats(request, collab_id):
    try:
        collab = cloudflare.get_collab(
            collab_id
        )["collab"]

        chats = cloudflare.list_chats(
            collab_id
        ).get("chats", [])

    except Exception as e:
        messages.error(
            request,
            f"Could not load chats: {e}",
        )

        return redirect(
            "collabs:detail",
            collab_id=collab_id,
        )

    return render(
        request,
        "collabs/chats.html",
        {
            "collab": collab,
            "chats": chats,
        },
    )