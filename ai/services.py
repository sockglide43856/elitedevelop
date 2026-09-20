import requests
from django.conf import settings


class AIServiceError(Exception):
    pass


def _worker_config():
    worker_url = getattr(settings, "AI_WORKER_URL", None)
    worker_secret = getattr(settings, "AI_WORKER_SECRET", None)

    if not worker_url:
        raise AIServiceError(
            "AI_WORKER_URL is not configured."
        )

    if not worker_secret:
        raise AIServiceError(
            "AI_WORKER_SECRET is not configured."
        )

    return worker_url, worker_secret


def queue_ai_job(
    job_id,
    model,
    system_prompt,
    messages,
):
    worker_url, worker_secret = _worker_config()

    payload = {
        "job_id": job_id,
        "model": model,
        "system_prompt": system_prompt,
        "messages": messages,
    }

    try:
        response = requests.post(
            worker_url,
            json=payload,
            headers={
                "Authorization": (
                    f"Bearer {worker_secret}"
                ),
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
            "AI worker returned an invalid response."
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
                "Authorization": (
                    f"Bearer {worker_secret}"
                ),
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
            "AI worker returned an invalid response."
        ) from exc