import secrets

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import AIRoom, AIMessage, AIJob
from .services import (
    AIServiceError,
    queue_ai_job,
    get_ai_job,
)


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
        },
    )


@login_required
@require_POST
def create_room(request):
    room = AIRoom.objects.create(
        user=request.user,
        name="New AI Room",
    )

    return JsonResponse({
        "success": True,
        "id": room.id,
        "name": room.name,
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
            "role": aimessage.role,
            "content": aimessage.content,
        }
        for aimessage in previous_messages
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

    job = AIJob.objects.create(
        room=ai_room,
        user=request.user,
        job_id=secrets.token_urlsafe(32),
        message=message,
    )

    try:
        queue_ai_job(
            job_id=job.job_id,
            model=ai_room.model,
            system_prompt=ai_room.system_prompt,
            messages=history,
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

    return JsonResponse({
        "success": True,
        "job_id": job.job_id,
        "status": "processing",
    })


@login_required
def job_status(request, job_id):
    job = get_object_or_404(
        AIJob,
        job_id=job_id,
        user=request.user,
    )

    try:
        data = get_ai_job(job.job_id)

    except AIServiceError as exc:
        return JsonResponse(
            {
                "success": False,
                "error": str(exc),
            },
            status=502,
        )

    status = data.get(
        "status",
        "processing",
    )

    if status == "completed":

        answer = data.get(
            "content",
            "",
        )

        if answer and job.status != "completed":

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

        return JsonResponse({
            "success": True,
            "status": "completed",
            "response": answer,
        })


    if status == "failed":

        error = data.get(
            "error",
            "AI request failed.",
        )

        job.status = "failed"
        job.error = error

        job.save(
            update_fields=[
                "status",
                "error",
            ]
        )

        return JsonResponse({
            "success": True,
            "status": "failed",
            "error": error,
        })


    return JsonResponse({
        "success": True,
        "status": status,
    })