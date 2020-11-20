from django.db import models


class Subscription(models.Model):
    """
    Subrsciption enthält die PSID eines User, der sich für die push-Benachrichtigungen am Morgen,
    Abend oder zu beiden Zeiten angemeldet hat.
    """

    class Meta:
        verbose_name = "Anmeldung"
        verbose_name_plural = "Anmeldungen"

    psid = models.CharField("PSID", max_length=200, null=False)

    morning = models.BooleanField("Morgen-Push", null=False, default=False)
    evening = models.BooleanField("Abend-Push", null=False, default=False)
