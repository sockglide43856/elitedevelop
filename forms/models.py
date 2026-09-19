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
    # secrets.token_hex(3) generates a 6-character hex string; we slice it to exactly 5 digits uppercase
    return secrets.token_hex(3)[:5].upper()

class FormConfiguration(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_forms', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, blank=True)

    # Secure, unguessable key strictly for the creator's dashboard access routing
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
        ('checkbox', 'Checkbox (True/False)')
    ]
    form = models.ForeignKey(FormConfiguration, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    is_required = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class FormSubmission(models.Model):
    form = models.ForeignKey(FormConfiguration, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

class FieldResponse(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='responses')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)