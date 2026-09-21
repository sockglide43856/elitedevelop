import base64
import hashlib
import hmac
import json
import time

import requests
from django.conf import settings


class AIServiceError(Exception):
    pass


def _worker_config():
    worker_url = getattr(settings, "AI_WORKER_URL", None)
    worker_secret = getattr(settings, "AI_WORKER_SECRET", None)

    if not worker_url:
        raise AIServiceError("AI_WORKER_URL is not configured.")

    if not worker_secret:
        raise AIServiceError("AI_WORKER_SECRET is not configured.")

    return worker_url.rstrip("/"), worker_secret


def queue_ai_job(
    job_id,
    model,
    system_prompt,
    messages,
    user_settings=None,
    user_memories=None,
    room_memories=None,
    page_context=None,
):
    worker_url, worker_secret = _worker_config()

    payload = {
        "job_id": job_id,
        "model": model,
        "system_prompt": system_prompt or "",
        "messages": messages,
        "user_settings": user_settings or {},
        "user_memories": user_memories or [],
        "room_memories": room_memories or [],
        "page_context": page_context or {},
    }

    try:
        response = requests.post(
            worker_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {worker_secret}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
    except requests.RequestException as exc:
        raise AIServiceError(
            f"AI worker unavailable: {exc}"
        ) from exc

    if not response.ok:
        try:
            data = response.json()
            error = data.get(
                "error",
                "Unable to queue AI request.",
            )
        except ValueError:
            error = (
                response.text
                or "Unable to queue AI request."
            )

        raise AIServiceError(error)

    try:
        data = response.json()
    except ValueError as exc:
        raise AIServiceError(
            "AI worker returned invalid JSON."
        ) from exc

    if not data.get("success"):
        raise AIServiceError(
            data.get(
                "error",
                "AI request was not queued.",
            )
        )

    return data


def get_ai_job(job_id):
    worker_url, worker_secret = _worker_config()

    try:
        response = requests.get(
            worker_url,
            params={
                "action": "status",
                "job_id": job_id,
            },
            headers={
                "Authorization": f"Bearer {worker_secret}"
            },
            timeout=5,
        )
    except requests.RequestException as exc:
        raise AIServiceError(
            f"AI worker unavailable: {exc}"
        ) from exc

    if not response.ok:
        try:
            data = response.json()
            error = data.get(
                "error",
                "Unable to check AI request.",
            )
        except ValueError:
            error = (
                response.text
                or "Unable to check AI request."
            )

        raise AIServiceError(error)

    try:
        return response.json()
    except ValueError as exc:
        raise AIServiceError(
            "AI worker returned invalid JSON."
        ) from exc


def create_stream_token(job_id, expires_in=300):
    _, secret = _worker_config()

    expires = int(time.time()) + expires_in

    payload = {
        "job_id": job_id,
        "exp": expires,
    }

    encoded = (
        base64.urlsafe_b64encode(
            json.dumps(
                payload,
                separators=(",", ":"),
            ).encode()
        )
        .decode()
        .rstrip("=")
    )

    signature = hmac.new(
        secret.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{encoded}.{signature}"