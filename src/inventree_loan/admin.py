"""Admin interfaces for the Loan app."""
from __future__ import unicode_literals

from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import LoanSession

admin.site.register(LoanSession, ImportExportModelAdmin)
