from django.contrib import admin
from .models import inDevelopment, UserProfile, UserBlock, UserReport, Organization, OrganizationMembership, OAuth2Key
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import UserProfile
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages
from .forms import SendEmailForm
from django.contrib import admin

from .models import ServerError


@admin.register(ServerError)
class ServerErrorAdmin(admin.ModelAdmin):
    list_display = (
        "error_code",
        "created_at",
        "exception_type",
        "method",
        "path",
        "user",
        "ip_address",
    )

    list_filter = (
        "created_at",
        "exception_type",
        "method",
    )

    search_fields = (
        "error_code",
        "exception_type",
        "exception_message",
        "traceback",
        "path",
        "query_string",
        "user__username",
        "user__email",
        "request_id",
    )

    readonly_fields = (
        "error_code",
        "created_at",
        "method",
        "path",
        "query_string",
        "user",
        "ip_address",
        "user_agent",
        "exception_type",
        "exception_message",
        "traceback",
        "metadata",
    )

    date_hierarchy = "created_at"

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Error",
            {
                "fields": (
                    "error_code",
                    "created_at",
                    "exception_type",
                    "exception_message",
                )
            },
        ),
        (
            "Request",
            {
                "fields": (
                    "method",
                    "path",
                    "query_string",
                    "user",
                    "ip_address",
                    "user_agent",
                )
            },
        ),
        (
            "Traceback",
            {
                "fields": (
                    "traceback",
                ),
            },
        ),
        (
            "Additional Metadata",
            {
                "fields": (
                    "metadata",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        # Errors should be created by the application,
        # not manually through the admin.
        return False

    def has_change_permission(self, request, obj=None):
        # These are diagnostic records; don't let staff accidentally modify them.
        return False
User = get_user_model()

@admin.action(description="Send custom email to selected users")
def send_custom_email(modeladmin, request, queryset):
    # Check if user submitted the intermediate form
    if 'apply' in request.POST:
        form = SendEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            recipient_list = [u.email for u in queryset if u.email]

            if recipient_list:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings.py
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
                modeladmin.message_user(
                    request,
                    f"Successfully sent email to {len(recipient_list)} user(s).",
                    messages.SUCCESS
                )
            else:
                modeladmin.message_user(
                    request,
                    "None of the selected users have valid email addresses.",
                    messages.WARNING
                )
            return None
    else:
        form = SendEmailForm()

    return render(
        request,
        'admin/send_email.html',
        {'users': queryset, 'form': form}
    )

# Register or override UserAdmin
class CustomUserAdmin(BaseUserAdmin):
    actions = [send_custom_email]

# If using default User model:
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
@staff_member_required
def approve_child_user(request, profile_id):
    profile = get_object_or_404(UserProfile, id=profile_id)

    # 1. Approve the account
    profile.is_approved = True

    # 2. Delete the physical PNG file from storage to stay compliant
    if profile.consent_form:
        profile.consent_form.delete(save=False) # Removes the file from the disk
        profile.consent_form = None             # Clears the database field

    profile.save()
    return redirect('admin_dashboard')
admin.site.register(inDevelopment)
admin.site.register(UserProfile)
admin.site.register(UserBlock)
admin.site.register(UserReport)
admin.site.register(OrganizationMembership)
admin.site.register(Organization)
admin.site.register(OAuth2Key)