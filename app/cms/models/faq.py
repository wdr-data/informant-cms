from django.db import models
from django.utils.text import slugify

from .attachment import HasAttachment
from .fragment import Fragment


class FAQ(HasAttachment):
    """
    FAQs werden über Payloads ausgespielt.
    """

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    name = models.CharField("Begriff", max_length=200, null=False)
    slug = models.CharField("Slug", max_length=200, null=True, blank=True)
    text = models.CharField("Intro-Text", max_length=2000, null=False)
    description = models.CharField("Beschreibung", max_length=400, blank=True)

    def __str__(self):
        return f"{self.name}"

    def _get_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 1
        while FAQ.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)


class FAQFragment(Fragment):
    class Meta:
        verbose_name = "FAQ-Fragment"
        verbose_name_plural = "FAQ-Fragmente"
        ordering = ("id",)

    faq = models.ForeignKey(
        "FAQ",
        on_delete=models.CASCADE,
        related_name="fragments",
        related_query_name="fragment",
    )
    link_faq = models.ForeignKey(
        "FAQ",
        on_delete=models.SET_NULL,
        related_name="+",
        related_query_name="+",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.faq.name} - {self.question}"
