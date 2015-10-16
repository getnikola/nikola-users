"""Admin registrations for Sites."""

from django.contrib import admin
from .models import Site, Language

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'language_code', 'country_code', 'display_country')

class SiteAdmin(admin.ModelAdmin):
    list_display = ('title', 'clickable_url', 'author_link_always', 'visible', 'featured')

    def make_visible(modeladmin, request, queryset):
        queryset.update(visible=True)

    make_visible.short_description = "Show selected sites"

    def make_invisible(modeladmin, request, queryset):
        queryset.update(visible=False)

    make_invisible.short_description = "Hide selected sites"

    actions = [make_visible, make_invisible]

admin.site.register(Site, SiteAdmin)
admin.site.register(Language, LanguageAdmin)