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

    NAVIGATION = [
        {'name': 'Loan Tracking', 'link': 'plugin:loan:tracking', 'icon': 'fas fa-clock'},
    ]

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
        from .forms import LoanSessionMaker
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
        from .urls import api_patterns
        from .views import LoanItemDetail, LoanTrackingDetail

        return [
            re_path(r'^hi/', self.view_test, name='hi'),
            re_path(r'^add/', self.add_loan, name='add'),
            re_path(r'^get/', self.get_loan, name='get'),
            re_path(r'^test/', LoanItemDetail.as_view(), name='test'),
            re_path(r'^api/', include(api_patterns), name="api"),
            re_path(r'^tracking/', LoanTrackingDetail.as_view(), name='tracking'),
            re_path(r'^', LoanTrackingDetail.as_view(), name='tracking')
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
        },
    }