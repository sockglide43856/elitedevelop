from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    electis_balance = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.user.username}: {self.electis_balance} Electis"


class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_p1')
    player2 = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='matches_as_p2')
    is_active = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    # Skip signal execution when loading fixtures (loaddata)
    if kwargs.get('raw'):
        return

    if created:
        Wallet.objects.get_or_create(user=instance)