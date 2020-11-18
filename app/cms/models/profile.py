from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profile"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    psid = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Facebook-ID",
        help_text="Sende #ich an den Bot, und trage die Zahl hier ein, "
        "um Meldungen und Pushes testen zu können.",
    )
    tgid = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Telegram-ID",
        help_text="Sende #ich an den Bot, und trage die Zahl hier ein, "
        "um Meldungen und Pushes testen zu können.",
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        return

    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
