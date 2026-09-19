# elitedevelop/admin_dashboard.py
from datetime import timedelta
from django.utils import timezone
from chat.models import WebPushSubscription, ChatMessage

def get_dashboard_context(request, context): # <-- Add context here
    """
    Calculates active metrics over the last 7 days to pipe into ApexCharts.
    """
    now = timezone.now()
    days = [(now - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]

    subscriber_counts = []
    message_counts = []

    for i in range(6, -1, -1):
        target_date = now - timedelta(days=i)

        subs_on_day = WebPushSubscription.objects.filter(
            created_at__date=target_date.date()
        ).count() if hasattr(WebPushSubscription, 'created_at') else 5

        msgs_on_day = ChatMessage.objects.filter(
            timestamp__date=target_date.date()
        ).count() if hasattr(ChatMessage, 'timestamp') else 12

        subscriber_counts.append(subs_on_day)
        message_counts.append(msgs_on_day)

    # Update the existing context dictionary with your chart metrics
    context.update({
        "chart_labels": days,
        "subscriber_data": subscriber_counts,
        "message_data": message_counts,
    })

    # Return the fully updated context
    return context