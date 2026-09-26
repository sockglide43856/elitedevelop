import requests
from django.conf import settings


def _request(method, path, **kwargs):
    url = f"{settings.COLLABS_API_URL.rstrip('/')}{path}"

    headers = kwargs.pop("headers", {})

    headers["Authorization"] = (
        f"Bearer {settings.COLLABS_API_KEY}"
    )

    response = requests.request(
        method,
        url,
        headers=headers,
        timeout=30,
        **kwargs,
    )

    try:
        data = response.json()
    except ValueError:
        data = {
            "ok": False,
            "error": response.text or "Invalid API response.",
        }

    if not response.ok:
        raise RuntimeError(
            data.get(
                "error",
                f"Cloudflare API returned HTTP {response.status_code}"
            )
        )

    return data


# =========================================================
# COLLABS
# =========================================================

def list_collabs(user_id):
    return _request(
        "GET",
        "/api/collabs",
        params={"user_id": user_id},
    )


def get_collab(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}",
    )


def create_collab(name, description, owner_id):
    return _request(
        "POST",
        "/api/collabs",
        json={
            "name": name,
            "description": description,
            "owner_id": owner_id,
        },
    )


def update_collab(collab_id, **fields):
    return _request(
        "PATCH",
        f"/api/collabs/{collab_id}",
        json=fields,
    )


def delete_collab(collab_id):
    return _request(
        "DELETE",
        f"/api/collabs/{collab_id}",
    )


# =========================================================
# DOCUMENTS
# =========================================================

def list_documents(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/docs",
    )


def create_document(
    collab_id,
    title,
    content,
    created_by,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/docs",
        json={
            "title": title,
            "content": content,
            "created_by": created_by,
        },
    )


def get_document(document_id):
    return _request(
        "GET",
        f"/api/documents/{document_id}",
    )


def update_document(
    document_id,
    title,
    content,
    user_id,
):
    return _request(
        "PATCH",
        f"/api/documents/{document_id}",
        json={
            "title": title,
            "content": content,
            "user_id": user_id,
        },
    )


def delete_document(
    document_id,
    user_id,
):
    return _request(
        "DELETE",
        f"/api/documents/{document_id}",
        params={
            "user_id": user_id,
        },
    )


# =========================================================
# FILES
# =========================================================

def list_files(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/files",
    )


def create_file(
    collab_id,
    name,
    mime_type,
    size,
    created_by,
    data=None,
    parent_id=None,
    is_directory=False,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/files",
        json={
            "name": name,
            "mime_type": mime_type,
            "size": size,
            "created_by": created_by,
            "data": data,
            "parent_id": parent_id,
            "is_directory": is_directory,
        },
    )


def get_file(file_id):
    return _request(
        "GET",
        f"/api/files/{file_id}",
    )


def update_file(
    file_id,
    user_id,
    name=None,
    parent_id=None,
):
    return _request(
        "PATCH",
        f"/api/files/{file_id}",
        json={
            "user_id": user_id,
            "name": name,
            "parent_id": parent_id,
        },
    )


def delete_file(
    file_id,
    user_id,
):
    return _request(
        "DELETE",
        f"/api/files/{file_id}",
        params={
            "user_id": user_id,
        },
    )


# =========================================================
# LINKS
# =========================================================

def list_links(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/links",
    )


def create_link(
    collab_id,
    title,
    url,
    created_by,
    pinned=False,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/links",
        json={
            "title": title,
            "url": url,
            "created_by": created_by,
            "pinned": pinned,
        },
    )


# =========================================================
# PINS
# =========================================================

def list_pins(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/pins",
    )


def create_pin(
    collab_id,
    item_type,
    item_id,
    title,
    created_by,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/pins",
        json={
            "item_type": item_type,
            "item_id": item_id,
            "title": title,
            "created_by": created_by,
        },
    )


# =========================================================
# ACTIVITY
# =========================================================

def list_activity(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/activity",
    )


# =========================================================
# MEMBERS
# =========================================================

def list_members(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/members",
    )


def add_member(
    collab_id,
    user_id,
    role,
    requested_by,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/members",
        json={
            "user_id": user_id,
            "role": role,
            "requested_by": requested_by,
        },
    )


# =========================================================
# INVITES
# =========================================================

def list_invites(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/invites",
    )


def create_invite(
    collab_id,
    created_by,
    role="viewer",
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/invites",
        json={
            "created_by": created_by,
            "role": role,
        },
    )


def join_invite(code, user_id):
    return _request(
        "POST",
        "/api/invites/join",
        json={
            "code": code,
            "user_id": user_id,
        },
    )


# =========================================================
# PRIVATE CHAT CONNECTION
# =========================================================

def list_chats(collab_id):
    return _request(
        "GET",
        f"/api/collabs/{collab_id}/chats",
    )


def connect_chat(
    collab_id,
    chat_room_id,
    user_id,
):
    return _request(
        "POST",
        f"/api/collabs/{collab_id}/chats",
        json={
            "chat_room_id": chat_room_id,
            "user_id": user_id,
        },
    )