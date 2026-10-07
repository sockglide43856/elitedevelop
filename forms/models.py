from django.db import models
from django.contrib.auth.models import User
import random
import string
import secrets

def generate_form_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not FormConfiguration.objects.filter(code=code).exists():
            return code

def generate_secret_token():
    return secrets.token_hex(3)[:5].upper()

class FormConfiguration(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_forms', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    secret_token = models.CharField(max_length=5, default=generate_secret_token, unique=True)
    title = models.CharField(max_length=200, default="My Custom Form")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_form_code()
        else:
            self.code = self.code.strip().replace(" ", "-").upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Short Text'),
        ('textarea', 'Long Paragraph'),
        ('number', 'Number'),
        ('email', 'Email Address'),
        ('checkbox', 'Checkbox (True/False)'),
        ('calender', 'Calendar Booking Slot')
    ]
    form = models.ForeignKey(FormConfiguration, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    calender_field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    calender_is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class CalenderAvailability(models.Model):
    SLOT_TYPE_CHOICES = [
        ('BLOCK', 'Fixed Block (Single Session)'),
        ('INTERVAL', 'Interval Spans (Split into smaller slots)'),
    ]

    form = models.ForeignKey(FormConfiguration, on_delete=models.CASCADE, related_name='availability_rules')
    # Store explicit datetimes so events can span multiple days or weeks
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPE_CHOICES, default='INTERVAL')
    interval_minutes = models.PositiveIntegerField(default=30)

class FormSubmission(models.Model):
    form = models.ForeignKey(FormConfiguration, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

class FieldResponse(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='responses')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)