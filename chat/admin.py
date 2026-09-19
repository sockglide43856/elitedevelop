from django import forms
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import WebPushSubscription, ChatMessage, PrivateMessage
from .utils import send_push_to_user

# ==========================================
# 1. BROADCAST INPUT FORM
# ==========================================
class CustomNotificationForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        initial="EliteDevelop Update 🚀",
        widget=forms.TextInput(attrs={
            'placeholder': 'Put the title for the notification here...',
            'style': 'width: 100%; max-width: 400px; padding: 6px; margin-bottom: 10px;'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'width: 100%; max-width: 400px; padding: 6px; margin-bottom: 10px;', 'placeholder': 'Type your terms update, privacy policy notice, or site updates here...'})
    )
    target_url = forms.CharField(
        max_length=200,
        initial="/",
        help_text="Where should users land when they tap the notification? (e.g., /chat/ or /privacy/)",
        widget=forms.TextInput(attrs={'style': 'width: 100%; max-width: 400px; padding: 6px;'})
    )

# ==========================================
# 2. UPGRADED INTERMEDIATE ADMIN ACTION
# ==========================================
@admin.action(description='📢 Broadcast Custom Notification to Selected Users')
def send_custom_broadcast(modeladmin, request, queryset):
    # If the user clicked "Launch Notification Broadcast" on the custom form
    if 'apply' in request.POST:
        form = CustomNotificationForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            message_text = form.cleaned_data['message']
            target_url = form.cleaned_data['target_url']

            # Extract unique users from selected subscriptions to avoid duplicate pings
            unique_users = set([sub.user for sub in queryset])
            success_count = 0

            for user in unique_users:
                # Fire the push notifications using our utility engine
                pushed = send_push_to_user(
                    user=user,
                    title=title,
                    message=message_text,
                    target_url=target_url
                )
                success_count += pushed

            if success_count > 0:
                modeladmin.message_user(
                    request,
                    f"Successfully broadcasted custom notification to {success_count} device(s)!",
                    messages.SUCCESS
                )
            else:
                modeladmin.message_user(
                    request,
                    "Failed to deliver notifications. 0 devices updated. Check PythonAnywhere logs.",
                    messages.ERROR
                )

            return HttpResponseRedirect(request.get_full_path())

    else:
        # If they just selected rows and clicked "Go", show them the empty layout form
        form = CustomNotificationForm()

    # Render the Django intermediate template page
    return render(request, 'admin/custom_notification_form.html', context={
        'subscriptions': queryset,
        'form': form,
        'action': 'send_custom_broadcast',
        'title': 'Compose Custom PWA Broadcast',
        'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME
    })

# ==========================================
# 3. ADMIN PANEL REGISTRATION
# ==========================================
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'created_at') if hasattr(WebPushSubscription, 'created_at') else ('user', 'endpoint')
    search_fields = ('user__username', 'endpoint')
    actions = [send_custom_broadcast]

admin.site.register(WebPushSubscription, WebPushSubscriptionAdmin)
admin.site.register(ChatMessage)
admin.site.register(PrivateMessage)