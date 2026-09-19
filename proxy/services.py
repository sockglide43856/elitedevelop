from django.db import transaction
from django.utils import timezone

from elitedevelop.models import UserProfile


def consume_proxy_request(user):
    """
    Atomically consume one proxy request.

    Returns:
        (True, remaining)
        (False, 0)
    """

    today = timezone.localdate()

    with transaction.atomic():

        profile = (
            UserProfile.objects
            .select_for_update()
            .get(user=user)
        )

        # New day → reset quota.
        if profile.proxy_requests_reset_date != today:
            profile.proxy_requests_today = 0
            profile.proxy_requests_reset_date = today

        # Quota exhausted.
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

            return False, 0

        # Consume exactly one request.
        profile.proxy_requests_today += 1

        profile.save(
            update_fields=[
                "proxy_requests_today",
                "proxy_requests_reset_date",
            ]
        )

        remaining = (
            profile.proxy_requests_per_day
            - profile.proxy_requests_today
        )

        return True, remaining