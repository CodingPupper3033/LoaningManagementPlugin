"""Admin interfaces for the Loan app."""
from __future__ import unicode_literals

from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import LoanUser, LoanSession


class InventoryLevelAdmin(ImportExportModelAdmin):
    """Admin interface for the InventoryLevel model."""

    list_display = (
        "location_id",
        "variant",
        "available",
    )
    list_filter = ("location_id",)


admin.site.register(LoanUser, ImportExportModelAdmin)
admin.site.register(LoanSession, ImportExportModelAdmin)
