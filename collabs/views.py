from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import cloudflare

User = get_user_model()

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

    return render(
        request,
        "collabs/files.html",
        {
            "collab": collab,
            "files": files,
        },
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