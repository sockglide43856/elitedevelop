import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from elitedevelop.models import UserProfile


TOKEN_LIFETIME = 60 * 60 * 24  # 24 hours
WORKER_AUTH_WINDOW = 90        # seconds

HISTORY_LIMIT = 20
HISTORY_CACHE_SECONDS = 60 * 60 * 24 * 7

User = get_user_model()


def create_proxy_token(user):
    """
    Create a signed 24-hour proxy session token.

    IMPORTANT:
    The destination URL is NOT stored in the token.
    The token belongs to the user/session only.
    """

    payload = {
        "exp": int(time.time()) + TOKEN_LIFETIME,
        "user_id": user.id,
    }

    payload_json = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    payload_b64 = (
        base64.urlsafe_b64encode(payload_json)
        .decode("ascii")
        .rstrip("=")
    )

    signature = hmac.new(
        settings.PROXY_WORKER_SECRET.encode("utf-8"),
        payload_b64.encode("ascii"),
        hashlib.sha256,
    ).digest()

    signature_b64 = (
        base64.urlsafe_b64encode(signature)
        .decode("ascii")
        .rstrip("=")
    )

    return f"{payload_b64}.{signature_b64}"


def reset_profile_if_needed(profile):
    today = timezone.localdate()

    if profile.proxy_requests_reset_date != today:
        profile.proxy_requests_today = 0
        profile.proxy_requests_reset_date = today

        profile.save(
            update_fields=[
                "proxy_requests_today",
                "proxy_requests_reset_date",
            ]
        )


def history_cache_key(user_id):
    return f"proxy-history:{user_id}"


def add_history(user_id, method, url):
    history = cache.get(
        history_cache_key(user_id),
        [],
    )

    history.insert(
        0,
        {
            "method": method,
            "url": url,
            "created_at": timezone.now(),
        },
    )

    history = history[:HISTORY_LIMIT]

    cache.set(
        history_cache_key(user_id),
        history,
        HISTORY_CACHE_SECONDS,
    )


@login_required
def index(request):
    profile = request.user.profile

    reset_profile_if_needed(profile)

    remaining = max(
        0,
        profile.proxy_requests_per_day
        - profile.proxy_requests_today,
    )

    return render(
        request,
        "proxy/index.html",
        {
            "profile": profile,
            "remaining": remaining,
        },
    )


@login_required
def token(request):
    """
    Creates a 24-hour proxy session token.

    This endpoint does NOT consume a request.

    The actual request is consumed when the Worker
    authorizes the top-level document navigation.
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    profile = request.user.profile

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400,
        )

    target_url = str(
        data.get("url", "")
    ).strip()

    if not target_url:
        return JsonResponse(
            {"error": "Missing URL."},
            status=400,
        )

    if not (
        target_url.startswith("http://")
        or target_url.startswith("https://")
    ):
        return JsonResponse(
            {
                "error":
                    "Only HTTP and HTTPS URLs are supported."
            },
            status=400,
        )

    reset_profile_if_needed(profile)

    if (
        profile.proxy_requests_today
        >= profile.proxy_requests_per_day
    ):
        return JsonResponse(
            {
                "error":
                    "Daily proxy request limit reached.",
                "remaining": 0,
            },
            status=429,
        )

    token_value = create_proxy_token(
        request.user
    )

    remaining = max(
        0,
        profile.proxy_requests_per_day
        - profile.proxy_requests_today,
    )

    return JsonResponse(
        {
            "token": token_value,
            "url": target_url,
            "remaining": remaining,
        }
    )


@csrf_exempt
def authorize_navigation(request):
    """
    Cloudflare Worker -> Django authorization endpoint.

    Every top-level document navigation consumes
    exactly one request.

    Images, CSS, JS, fonts, etc. do not consume quota.
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405,
        )

    secret = getattr(
        settings,
        "PROXY_WORKER_SECRET",
        "",
    )

    if not secret:
        return JsonResponse(
            {
                "error":
                    "Worker authentication is not configured."
            },
            status=500,
        )

    try:
        data = json.loads(request.body)

        user_id = int(data["user_id"])
        target_url = str(
            data["url"]
        ).strip()

        timestamp = int(
            data["timestamp"]
        )

        signature = str(
            data["signature"]
        ).strip()

        method = str(
            data.get("method", "GET")
        ).upper()

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ):
        return JsonResponse(
            {
                "error":
                    "Invalid authorization request."
            },
            status=400,
        )

    # -----------------------------------------------------
    # Validate timestamp
    # -----------------------------------------------------

    now = int(time.time())

    if abs(now - timestamp) > WORKER_AUTH_WINDOW:
        return JsonResponse(
            {
                "error":
                    "Authorization request expired."
            },
            status=403,
        )

    # -----------------------------------------------------
    # Validate URL
    # -----------------------------------------------------

    if not (
        target_url.startswith("http://")
        or target_url.startswith("https://")
    ):
        return JsonResponse(
            {
                "error":
                    "Only HTTP and HTTPS URLs are supported."
            },
            status=400,
        )

    # -----------------------------------------------------
    # Re-create EXACTLY the same canonical string
    # used by the Cloudflare Worker.
    #
    # Worker:
    #
    # `${timestamp}.${userId}.${targetURL}`
    #
    # Django:
    #
    # f"{timestamp}.{user_id}.{target_url}"
    # -----------------------------------------------------

    canonical = (
        f"{timestamp}.{user_id}.{target_url}"
    )

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    # -----------------------------------------------------
    # Decode Worker's URL-safe Base64 signature.
    # -----------------------------------------------------

    try:
        if not signature:
            raise ValueError(
                "Empty signature"
            )

        # Reject characters that cannot occur in
        # URL-safe Base64.
        allowed_chars = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            "-_="
        )

        if any(
            character not in allowed_chars
            for character in signature
        ):
            raise ValueError(
                "Invalid Base64 characters"
            )

        # Restore Base64 padding.
        padded_signature = (
            signature
            + "=" * (-len(signature) % 4)
        )

        provided_signature = (
            base64.urlsafe_b64decode(
                padded_signature.encode("ascii")
            )
        )

    except (
        ValueError,
        UnicodeEncodeError,
        base64.binascii.Error,
    ):
        return JsonResponse(
            {
                "error":
                    "Invalid authorization signature."
            },
            status=403,
        )

    # HMAC-SHA256 signatures must be exactly 32 bytes.
    if len(provided_signature) != 32:
        return JsonResponse(
            {
                "error":
                    "Invalid authorization signature."
            },
            status=403,
        )

    # -----------------------------------------------------
    # Compare signatures safely.
    # -----------------------------------------------------

    if not hmac.compare_digest(
        expected_signature,
        provided_signature,
    ):
        return JsonResponse(
            {
                "error":
                    "Invalid Worker authorization."
            },
            status=403,
        )

    # -----------------------------------------------------
    # Find user.
    # -----------------------------------------------------

    try:
        user = User.objects.get(
            id=user_id
        )
    except User.DoesNotExist:
        return JsonResponse(
            {
                "error":
                    "User not found."
            },
            status=403,
        )

    # -----------------------------------------------------
    # Atomically consume one request.
    # -----------------------------------------------------

    with transaction.atomic():

        profile = (
            UserProfile.objects
            .select_for_update()
            .get(user=user)
        )

        today = timezone.localdate()

        if (
            profile.proxy_requests_reset_date
            != today
        ):
            profile.proxy_requests_today = 0
            profile.proxy_requests_reset_date = today

        if (
            profile.proxy_requests_today
            >= profile.proxy_requests_per_day
        ):
            profile.save(
                update_fields=[
                    "proxy_requests_today",
                    "proxy_requests_reset_date",
                ]
            )

            return JsonResponse(
                {
                    "allowed": False,
                    "error":
                        "Daily proxy request limit reached.",
                    "remaining": 0,
                },
                status=429,
            )

        profile.proxy_requests_today += 1

        profile.save(
            update_fields=[
                "proxy_requests_today",
                "proxy_requests_reset_date",
            ]
        )

        remaining = max(
            0,
            profile.proxy_requests_per_day
            - profile.proxy_requests_today,
        )

    # -----------------------------------------------------
    # Save history.
    # -----------------------------------------------------

    add_history(
        user_id,
        method,
        target_url,
    )

    return JsonResponse(
        {
            "allowed": True,
            "remaining": remaining,
        }
    )