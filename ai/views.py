import secrets

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    AIJob,
    AIMessage,
    AIRoom,
    AIRoomMemory,
    AIUserMemory,
    AIUserSettings,
)
from .services import (
    AIServiceError,
    create_stream_token,
    queue_ai_job,
)


def get_user_ai_settings(user):
    apex_settings, _ = AIUserSettings.objects.get_or_create(
        user=user
    )

    return apex_settings


@login_required
def rooms(request):
    user_rooms = AIRoom.objects.filter(
        user=request.user
    )

    return render(
        request,
        "ai/rooms.html",
        {
            "rooms": user_rooms,
        },
    )


@login_required
def room(request, room_id):
    ai_room = get_object_or_404(
        AIRoom,
        id=room_id,
        user=request.user,
    )

    return render(
        request,
        "ai/room.html",
        {
            "room": ai_room,
            "aimessages": ai_room.messages.all(),
            "room_memories": ai_room.memories.all(),
        },
    )


@login_required
@require_POST
def create_room(request):
    ai_room = AIRoom.objects.create(
        user=request.user,
        name="New AI Room",
    )

    return JsonResponse({
        "success": True,
        "id": ai_room.id,
        "name": ai_room.name,
    })


@login_required
@require_POST
def rename_room(request, room_id):
    ai_room = get_object_or_404(
        AIRoom,
        id=room_id,
        user=request.user,
    )

    name = request.POST.get(
        "name",
        "",
    ).strip()

    if not name:
        return JsonResponse(
            {
                "success": False,
                "error": "Room name cannot be empty.",
            },
            status=400,
        )

    if len(name) > 100:
        return JsonResponse(
            {
                "success": False,
                "error": "Room name is too long.",
            },
            status=400,
        )

    ai_room.name = name
    ai_room.save(
        update_fields=[
            "name",
            "updated_at",
        ]
    )

    return JsonResponse({
        "success": True,
        "name": ai_room.name,
    })


@login_required
@require_POST
def delete_room(request, room_id):
    ai_room = get_object_or_404(
        AIRoom,
        id=room_id,
        user=request.user,
    )

    ai_room.delete()

    return JsonResponse({
        "success": True,
    })


@login_required
@require_POST
def send_message(request, room_id):
    ai_room = get_object_or_404(
        AIRoom,
        id=room_id,
        user=request.user,
    )

    message = request.POST.get(
        "message",
        "",
    ).strip()

    if not message:
        return JsonResponse(
            {
                "success": False,
                "error": "Message cannot be empty.",
            },
            status=400,
        )

    if len(message) > 10000:
        return JsonResponse(
            {
                "success": False,
                "error": "Message is too long.",
            },
            status=400,
        )

    previous_messages = list(
        ai_room.messages
        .order_by("-created_at")[:30]
    )

    previous_messages.reverse()

    history = [
        {
            "role": aiMessage.role,
            "content": aiMessage.content,
        }
        for aiMessage in previous_messages
    ]

    AIMessage.objects.create(
        room=ai_room,
        role="user",
        content=message,
    )

    history.append({
        "role": "user",
        "content": message,
    })

    apex_settings = get_user_ai_settings(
        request.user
    )

    user_memories = []

    if apex_settings.memory_enabled:
        user_memories = list(
            AIUserMemory.objects.filter(
                user=request.user
            ).values_list(
                "content",
                flat=True,
            )
        )

    room_memories = []

    if ai_room.memory_enabled:
        room_memories = list(
            AIRoomMemory.objects.filter(
                room=ai_room
            ).values_list(
                "content",
                flat=True,
            )
        )

    user_settings = {
        "preferred_name":
            apex_settings.preferred_name,

        "title":
            apex_settings.title,

        "about":
            apex_settings.about,

        "instructions":
            apex_settings.instructions,
    }

    job = AIJob.objects.create(
        room=ai_room,
        user=request.user,
        job_id=secrets.token_urlsafe(32),
        message=message,
        status="queued",
    )

    try:
        queue_ai_job(
            job_id=job.job_id,
            model=ai_room.model,
            system_prompt=ai_room.system_prompt,
            messages=history,
            user_settings=user_settings,
            user_memories=user_memories,
            room_memories=room_memories,
        )

    except AIServiceError as exc:
        job.status = "failed"
        job.error = str(exc)

        job.save(
            update_fields=[
                "status",
                "error",
            ]
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=502,
        )

    job.status = "processing"

    job.save(
        update_fields=["status"]
    )

    stream_token = create_stream_token(
        job.job_id
    )

    worker_url = (
        settings.AI_WORKER_URL
        .rstrip("/")
    )

    stream_url = (
        f"{worker_url}"
        f"?action=stream"
        f"&job_id={job.job_id}"
        f"&token={stream_token}"
    )

    return JsonResponse({
        "success": True,
        "job_id": job.job_id,
        "status": "processing",
        "stream_url": stream_url,
    })


@login_required
@require_POST
def complete_job(request, job_id):
    job = get_object_or_404(
        AIJob,
        job_id=job_id,
        user=request.user,
    )

    if job.status == "completed":
        return JsonResponse({
            "success": True,
            "status": "completed",
            "response": job.response,
        })

    answer = request.POST.get(
        "response",
        "",
    )

    if not answer:
        return JsonResponse(
            {
                "success": False,
                "error": "Response cannot be empty.",
            },
            status=400,
        )

    AIMessage.objects.create(
        room=job.room,
        role="assistant",
        content=answer,
    )

    job.status = "completed"
    job.response = answer
    job.completed_at = timezone.now()

    job.save(
        update_fields=[
            "status",
            "response",
            "completed_at",
        ]
    )

    job.room.updated_at = timezone.now()

    job.room.save(
        update_fields=["updated_at"]
    )

    return JsonResponse({
        "success": True,
        "status": "completed",
    })


# ============================================================
# USER SETTINGS
# ============================================================

@login_required
def settings_view(request):
    apex_settings = get_user_ai_settings(
        request.user
    )

    memories = AIUserMemory.objects.filter(
        user=request.user
    )

    return render(
        request,
        "ai/settings.html",
        {
            "apex_settings": apex_settings,
            "memories": memories,
        },
    )


@login_required
@require_POST
def update_settings(request):
    apex_settings = get_user_ai_settings(
        request.user
    )

    apex_settings.preferred_name = (
        request.POST.get(
            "preferred_name",
            "",
        ).strip()
    )

    apex_settings.title = (
        request.POST.get(
            "title",
            "",
        ).strip()
    )

    apex_settings.about = (
        request.POST.get(
            "about",
            "",
        ).strip()
    )

    apex_settings.instructions = (
        request.POST.get(
            "instructions",
            "",
        ).strip()
    )

    apex_settings.memory_enabled = (
        request.POST.get(
            "memory_enabled"
        ) == "on"
    )

    apex_settings.save()

    return JsonResponse({
        "success": True,
    })


# ============================================================
# USER MEMORY
# ============================================================

@login_required
@require_POST
def create_user_memory(request):
    content = request.POST.get(
        "content",
        "",
    ).strip()

    if not content:
        return JsonResponse(
            {
                "success": False,
                "error": "Memory cannot be empty.",
            },
            status=400,
        )

    if len(content) > 2000:
        return JsonResponse(
            {
                "success": False,
                "error": "Memory is too long.",
            },
            status=400,
        )

    memory = AIUserMemory.objects.create(
        user=request.user,
        content=content,
    )

    return JsonResponse({
        "success": True,
        "id": memory.id,
        "content": memory.content,
    })


@login_required
@require_POST
def delete_user_memory(request, memory_id):
    memory = get_object_or_404(
        AIUserMemory,
        id=memory_id,
        user=request.user,
    )

    memory.delete()

    return JsonResponse({
        "success": True,
    })


# ============================================================
# ROOM MEMORY
# ============================================================

@login_required
@require_POST
def create_room_memory(request, room_id):
    ai_room = get_object_or_404(
        AIRoom,
        id=room_id,
        user=request.user,
    )

    content = request.POST.get(
        "content",
        "",
    ).strip()

    if not content:
        return JsonResponse(
            {
                "success": False,
                "error": "Memory cannot be empty.",
            },
            status=400,
        )

    if len(content) > 2000:
        return JsonResponse(
            {
                "success": False,
                "error": "Memory is too long.",
            },
            status=400,
        )

    memory = AIRoomMemory.objects.create(
        room=ai_room,
        content=content,
    )

    return JsonResponse({
        "success": True,
        "id": memory.id,
        "content": memory.content,
    })


@login_required
@require_POST
def delete_room_memory(request, memory_id):
    memory = get_object_or_404(
        AIRoomMemory,
        id=memory_id,
        room__user=request.user,
    )

    memory.delete()

    return JsonResponse({
        "success": True,
    })