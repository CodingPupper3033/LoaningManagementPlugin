"""Plugin to provide stock loaning capabilities within Inventree."""

import logging

from django.core.validators import MinValueValidator
from django.http import HttpResponse, JsonResponse
from django.urls import include, re_path, path
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.views.generic import RedirectView

from plugin import InvenTreePlugin
from stock.models import StockItem
from plugin.mixins import AppMixin, NavigationMixin, SettingsMixin, UrlsMixin, ActionMixin, PanelMixin
from stock.views import StockItemDetail


logger = logging.getLogger('inventree')

class LoanPlugin(ActionMixin, AppMixin, SettingsMixin, UrlsMixin, NavigationMixin, PanelMixin,InvenTreePlugin):
    """Main plugin class for loaning capabilities."""

    # Plugin Metadata
    NAME = "LoanPlugin"
    SLUG = "loan"
    TITLE = "Loan Management"
    DESCRIPTION = "A plugin to manage loaning and tracking stock items."
    VERSION = "2024-06-04"
    AUTHOR = "Joshua Miller, Kyle Wilt @ RPI"
    ROLE = "sales_order"

    # Navigation
    NAVIGATION_TAB_NAME = "Loan"
    NAVIGATION_TAB_ICON = 'fas fa-handshake'

    NAVIGATION = [
        {
            'name': 'Loan Tracking',
            'link': 'plugin:loan:tracking',
            'icon': 'fas fa-clock',
            'role': 'sales_order.view',
        },
    ]
        
    # Settings
    SETTINGS = {
        'DEFAULT_LOAN_DURATION_DAYS': {
            'name': _('Default Loan Duration'),  # TODO Rewrite
            'description': "The default duration an item will be loaned for in days.",  # TODO Rewrite
            'default': 28,
            'validator': [
                int,
                MinValueValidator(0)
            ]
        },
        'USER_LOOKUP_API': {
            'name': _('User Lookup API URL'),
            'description': _("Internal API for loan user lookup. This is expected to be provided by a corresponding plugin. Alternatively, this plugin could be modified to use the APICallMixin to directly interface with an external server."),
            'default': ""
        },
    }
    
    # Get user lookup api, if it exists
    @property
    def userlookup_api_url(self):
        #if self.get_setting("USER_LOOKUP_API"):
        #    return "{}".format(self.get_setting("USER_LOOKUP_API"))
        #return False
        return "{}".format(self.get_setting("USER_LOOKUP_API"))

    # Custom Panels
    STOCK_ITEM_LOAN_PANEL_TITLE = "Loan History"
    
    def get_custom_panels(self, view, request):
        panels = []

        # Stock Item Loaning information panel
        if isinstance(view, StockItemDetail):
            panels.append({
                "title": LoanPlugin.STOCK_ITEM_LOAN_PANEL_TITLE,
                "icon": "fas fa-handshake",
                "content_template": "loaning_stats_panel.html",
                #"javascript_template": "js/track.js",
                "javascript_template": "js/loan.js",
                "role": LoanPlugin.ROLE,
                "badge_api":LoanPlugin.userlookup_api_url,
            })

        return panels

    # URL Patterns for the plugin
    def setup_urls(self):
        from .urls import api_patterns
        from .views import LoanItemDetail, LoanTrackingDetail

        return [
            re_path(r'^api/', include(api_patterns), name="api"),
            re_path(r'^tracking/', LoanTrackingDetail.as_view(), name='tracking'),
            re_path(r'^', LoanTrackingDetail.as_view(), name='tracking')
        ]
