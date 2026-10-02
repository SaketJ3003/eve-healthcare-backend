from django.contrib import admin

from .models import DiagnosticCentre, DiagnosticTest


@admin.register(DiagnosticCentre)
class DiagnosticCentreAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "location",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "location")
    list_filter = ("is_active",)


@admin.register(DiagnosticTest)
class DiagnosticTestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "centre",
        "price",
        "is_active",
    )
    search_fields = ("name", "centre__name")
    list_filter = ("is_active", "centre")