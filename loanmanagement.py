import logging

from django.core.validators import MinValueValidator
from django.http import HttpResponse, JsonResponse
from django.urls import include, re_path, path
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from plugin import InvenTreePlugin
from .forms import LoanSessionMaker
from stock.models import StockItem
from plugin.mixins import AppMixin, NavigationMixin, SettingsMixin, UrlsMixin, ActionMixin, PanelMixin
from stock.views import StockItemDetail


class LoaningManagementPlugin(AppMixin, ActionMixin, SettingsMixin, UrlsMixin, NavigationMixin, PanelMixin,
                              InvenTreePlugin):
    """
    Adds loaning management functionality to InvenTree.
    """

    NAME = "Loan Management"
    SLUG = "loan"
    TITLE = "Loan Management"
    DESCRIPTION = "A plugin to manage loaning and tracking stock"
    VERSION = "0.0.1"
    AUTHOR = "Joshua Miller, Kyle Wilt @ RPI"

    # Navigation
    NAVIGATION_TAB_NAME = "Loan"
    NAVIGATION_TAB_ICON = 'fas fa-exchange-alt'

    # Stock Metadata
    STOCK_KEY_LOANED_STATE = SLUG + "_" + "loaned_state"
    STOCK_KEY_DEFAULTS = {
        STOCK_KEY_LOANED_STATE: False
    }

    # Custom Panels
    STOCK_ITEM_LOAN_PANEL_TITLE = "Loaning"

    def get_custom_panels(self, view, request):
        panels = []

        # Stock Item View
        if isinstance(view, StockItemDetail):
            panels.append({
                "title": LoaningManagementPlugin.STOCK_ITEM_LOAN_PANEL_TITLE,
                "icon": "fas fa-handshake",
                "content_template": "loaningmanagement/loaning_stats_panel.html",
            })

        return panels

    def view_test(self, request):
        items = StockItem.objects.all()

        # print(list(animes.values()))

        #from common.models import InvenTreeSetting
        data = {
            'items': list(items.values()),
            #'models': list(model.__name__ for model in apps.get_models()),
            #'apps': list(app.verbose_name for app in apps.get_app_configs()),
            #'add_date': getDefaultDueDate()
        }

        return JsonResponse(data)
        """Very basic view."""
        return HttpResponse(f'Loaned State for stock item 69: {self.get_loaned_state(69)}')

    def add_loan(self, request):

        context = {
            'form': LoanSessionMaker()
        }
        #return render(request, 'add.html', context)
        return render(request, 'loansessionform_temp.html', context)

    def get_loan(self, request):
        from .models import LoanSession
        loans = LoanSession.objects.all()

        # print(list(animes.values()))

        data = {
            'loans': list(loans.values())
        }

        return JsonResponse(data)

    def setup_urls(self):
        from . import api
        loan_session_api_urls = [
            path(r'<int:pk>/', include([
                re_path(r'^.*$', api.LoanSessionDetail.as_view(), name='api-part-detail')
            ])),
            re_path(r'^.*$', api.LoanSessionList.as_view(), name='api-loan-session-list'),
        ]

        return [
            re_path(r'^hi/', self.view_test, name='hi'),
            re_path(r'^add/', self.add_loan, name='add'),
            re_path(r'^get/', self.get_loan, name='get'),
            re_path(r'^api/', include(loan_session_api_urls), name="api"),
            # re_path(r'^test/', api.LoanSessionList.as_view(), name='api-loan-session-list')
        ]

    SETTINGS = {
        'DEFAULT_LOAN_DURATION_DAYS': {
            'name': _('Default Loan Duration'),  # TODO Rewrite
            'description': "The default duration an item will be loaned for in days.",  # TODO Rewrite
            'default': 28,
            'validator': [
                int,
                MinValueValidator(0)
            ]
        }
    }

    NAVIGATION = [
        {'name': 'Loaned Devices', 'link': 'plugin:loan:hi', 'icon': 'fas fa-list'},
    ]