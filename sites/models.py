"""Models for sites and languages."""

from django.db import models
from django.utils.html import format_html, mark_safe, escape


class Language(models.Model):
    """A language model."""

    name = models.CharField("Display name", max_length=50, unique=True)
    language_code = models.CharField("Language code", max_length=5)
    country_code = models.CharField("Country code", max_length=5)
    display_country = models.BooleanField(default=False)

    @property
    def code(self):
        if self.display_country:
            return '_'.join((self.language_code, self.country_code))
        else:
            return self.language_code

    def __str__(self):
        """String representation of a language."""
        return "{0} [{1}]".format(self.name, self.code)


class Site(models.Model):
    """A site model."""

    title = models.CharField(max_length=100)
    url = models.URLField("Site URL", max_length=512, unique=True)
    author = models.CharField(max_length=100)
    description = models.TextField(max_length=512)
    sourcelink = models.URLField("Source link", max_length=512, blank=True)
    date = models.DateTimeField("Date added", auto_now_add=True)
    languages = models.ManyToManyField(Language)
    visible = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    featured_order = models.IntegerField("Order (for featured sites)", blank=True, null=True)
    featured_reason = models.TextField("Reason (for featured sites)", max_length=100, blank=True)

    def clickable_url(self):
        return format_html('<a href="{0}" rel="nofollow">{0}</a>', self.url)

    @property
    def link(self):
        return format_html('<a href="{0}" rel="nofollow">{1}</a>', self.url,
                           self.title)

    @property
    def clickable_sourcelink(self):
        return format_html('<a href="{0}" rel="nofollow">Source</a>',
                           self.sourcelink)

    @property
    def description_formatted(self):
        return mark_safe(escape(self.description).replace('\n\n', '<p>').replace('\n', '<br>'))

    clickable_url.short_description = 'URL'
    clickable_url = property(clickable_url)

    def __str__(self):
        """String representation of a site."""
        return self.title


class BlacklistedURL(models.Model):
    """A blacklisted URL or URL fragment."""
    url = models.CharField("URL", max_length=512, unique=True)
    exact = models.BooleanField("Exact match", default=False)

    def __str__(self):
        """String representation of a blacklisted URL."""
        return self.url

    def __repr__(self):
        """Representation of a blacklisted URL."""
        return "<{} (exact: {})>".format(self.url, self.exact)

    class Meta:
        verbose_name = "blacklisted URL"
        verbose_name_plural = "blacklisted URLs"
