import json
from pywebpush import webpush, WebPushException
from .models import WebPushSubscription

# Cryptographic keys matched directly to your verified public_key setup
VAPID_PRIVATE_KEY = "JrRSvxUFwjqiFkNyS1WsK1t8Y1s4i+LrxgGLthpxdQe="
VAPID_ADMIN_EMAIL = "mailto:threedio@outlook.com"

def send_push_to_user(user, title, message, target_url=None):
    """
    Finds all active web push subscription records for a given user
    and pushes out payload bundles to their device endpoints.
    """
    subscriptions = WebPushSubscription.objects.filter(user=user)

    payload = {
        "title": title,
        "message": message,
        "url": target_url if target_url else "/chat/"
    }

    payload_string = json.dumps(payload)
    success_count = 0

    for sub in subscriptions:
        try:
            # Construct standard WebPush dictionary structure
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }

            webpush(
                subscription_info=subscription_info,
                data=payload_string,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_ADMIN_EMAIL}
            )
            success_count += 1

        except WebPushException as ex:
            print(f"WebPush delivery error caught for user {user.username}: {ex}")
            # Optional: Delete subscription record if it has expired/uninstalled (410 Gone response)
            if ex.response and ex.response.status_code == 410:
                sub.delete()
        except Exception as e:
            print(f"Generic notification error caught: {e}")

    return success_count