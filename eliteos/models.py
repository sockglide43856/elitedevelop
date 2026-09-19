from django.conf import settings
from django.db import models


class OSProfile(models.Model):
    """
    Stores persistent EliteOS settings for each user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eliteos_profile",
    )

    display_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    wallpaper = models.CharField(
        max_length=500,
        default=(
            "radial-gradient(circle at 20% 20%, #4f7cff 0%, transparent 30%), "
            "radial-gradient(circle at 80% 25%, #7c3aed 0%, transparent 32%), "
            "radial-gradient(circle at 50% 100%, #0ea5e9 0%, transparent 40%), "
            "linear-gradient(135deg, #06111f, #0d1d33)"
        ),
    )

    accent = models.CharField(
        max_length=30,
        default="#4f7cff",
    )

    theme = models.CharField(
        max_length=20,
        default="dark",
    )

    panel_position = models.CharField(
        max_length=20,
        default="bottom",
    )

    transparency = models.PositiveIntegerField(
        default=78,
    )

    animations = models.BooleanField(
        default=True,
    )

    boot_count = models.PositiveBigIntegerField(
        default=0,
    )

    last_booted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"EliteOS profile: {self.user}"


class OSFilesystem(models.Model):
    """
    Stores a compressed JSON virtual filesystem.
    """

    MAX_COMPRESSED_SIZE = 1024 * 1024

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eliteos_filesystem",
    )

    image = models.BinaryField(
        default=bytes,
    )

    compressed_size = models.PositiveIntegerField(
        default=0,
    )

    filesystem_version = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @property
    def size_limit(self):
        return self.MAX_COMPRESSED_SIZE

    def __str__(self):
        return f"EliteOS filesystem: {self.user}"


class InstalledApp(models.Model):
    """
    Apps installed by a specific user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eliteos_installed_apps",
    )

    app_id = models.CharField(
        max_length=100,
    )

    installed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "app_id"],
                name="eliteos_unique_installed_app",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.app_id}"


class StoreApp(models.Model):
    """
    Applications available through the EliteOS App Store.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("published", "Published"),
        ("rejected", "Rejected"),
    ]

    app_id = models.CharField(
        max_length=100,
        unique=True,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eliteos_store_apps",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    icon = models.CharField(
        max_length=20,
        default="◈",
    )

    version = models.CharField(
        max_length=30,
        default="1.0.0",
    )

    source = models.JSONField(
        default=dict,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    downloads = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.app_id})"


class OSNotification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="eliteos_notifications",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        default="info",
    )

    read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user}: {self.title}"