from django.conf import settings
from django.db import models


class AIRoom(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_rooms",
    )

    name = models.CharField(
        max_length=100,
        default="New AI Room",
    )

    model = models.CharField(
        max_length=200,
        default="nvidia/nemotron-3-ultra-550b-a55b:free",
    )

    system_prompt = models.TextField(
        blank=True,
        default="",
    )

    memory_enabled = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} — {self.user}"


class AIMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    room = models.ForeignKey(
        AIRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIJob(models.Model):
    STATUS_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    room = models.ForeignKey(
        AIRoom,
        on_delete=models.CASCADE,
        related_name="jobs",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_jobs",
    )

    job_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="queued",
    )

    response = models.TextField(
        blank=True,
        default="",
    )

    error = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.job_id} — {self.status}"


class AIUserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_settings",
    )

    preferred_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    title = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    about = models.TextField(
        blank=True,
        default="",
    )

    instructions = models.TextField(
        blank=True,
        default="",
    )

    memory_enabled = models.BooleanField(
        default=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Apex settings — {self.user}"


class AIUserMemory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_memories",
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"User memory — {self.content[:60]}"


class AIRoomMemory(models.Model):
    room = models.ForeignKey(
        AIRoom,
        on_delete=models.CASCADE,
        related_name="memories",
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Room memory — {self.content[:60]}"