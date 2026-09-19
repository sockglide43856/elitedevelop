from django.contrib import admin
from .models import FormConfiguration, FormField, FormSubmission, FieldResponse

class FormFieldInline(admin.TabularInline):
    """Allows you to view and edit custom fields directly inside the Form page."""
    model = FormField
    extra = 1
    fields = ['label', 'field_type', 'is_required', 'order']

@admin.register(FormConfiguration)
class FormConfigurationAdmin(admin.ModelAdmin):
    # What columns show up when looking at the complete list of forms
    list_display = ('title', 'code', 'secret_token', 'creator', 'created_at')

    # Adds a search bar to filter by title, public code, secret token, or creator username
    search_fields = ('title', 'code', 'secret_token', 'creator__username')

    # Adds a filter sidebar on the right side
    list_filter = ('created_at', 'creator')

    # Embeds the questions directly below the main form settings
    inlines = [FormFieldInline]

class FieldResponseInline(admin.TabularInline):
    """Allows you to see the actual answers inside the submission view."""
    model = FieldResponse
    extra = 0
    readonly_fields = ['field', 'answer']
    can_delete = False

@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('form', 'submitted_at')
    list_filter = ('form', 'submitted_at')
    inlines = [FieldResponseInline]

# Basic registration for reading raw field assets and individual answers if needed
admin.site.register(FormField)
admin.site.register(FieldResponse)