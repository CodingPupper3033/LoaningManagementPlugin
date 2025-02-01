"""Plugin to provide stock loaning capabilities within Inventree."""

import logging

from django.core.validators import MinValueValidator
from django.http import HttpResponse, JsonResponse
from django.urls import include, re_path, path
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.views.generic import RedirectView

from InvenTree.email import send_email
from plugin import InvenTreePlugin
from stock.models import StockItem
from part.models import Part
from plugin.mixins import AppMixin, NavigationMixin, SettingsMixin, UrlsMixin, ActionMixin, PanelMixin, ScheduleMixin
from stock.views import StockItemDetail
from part.views import PartDetail
from .models import LoanSession
from users.serializers import RoleSerializer
from users.models import check_user_role

from datetime import date


logger = logging.getLogger('inventree')

class LoanPlugin(ActionMixin, AppMixin, SettingsMixin, UrlsMixin, NavigationMixin, PanelMixin, ScheduleMixin, InvenTreePlugin):
    """Main plugin class for loaning capabilities."""

    # Plugin Metadata
    NAME = "LoanPlugin"
    SLUG = "loan"
    TITLE = "Loan Management"
    DESCRIPTION = "A plugin to manage loaning and tracking stock items."
    VERSION = "2025-01-31-emailbeta"
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
        'UNLOANABLE_SUFFIX': {
            'name': _('Unloanable serial Suffix'),
            'description': _("Optional added suffix to a stock item which renders the part unloanable"),
            'default': "",
        },
        'USER_LOOKUP_API': {
            'name': _('User Lookup API URL'),
            'description': _("Internal API for loan user lookup. This is expected to be provided by a corresponding plugin. Alternatively, this plugin could be modified to use the APICallMixin to directly interface with an external server."),
            'default': ""
        },
        'ENABLE_OVERDUE_EMAIL': {
            'name': _('Enable Overdue Email'),
            'description': _("Server will send e-mail when loan is overdue and again every X days afterwards, set by 'Overdue Notice Frequency'"),
            'validator': bool,
            'default': False,
        },
        'OVERDUE_NOTICE_FREQ': {
            'name': _('Overdue Notice Frequency'),
            'description': _("Sets how often an overdue notice is sent, in days"),
            'default':7,
            'validator': [
                int,
                MinValueValidator(1)
            ],
        },
    }

    SCHEDULED_TASKS = {
        'check_late' : {
            'func' : 'check_late',
            'schedule' : 'D',
#            'schedule' : 'I',
#            'minutes' : 10,
        },
    }
    
        
    # Get user lookup api, if it exists
    @property
    def userlookup_api_url(self):
        #if self.get_setting("USER_LOOKUP_API"):
        #    return "{}".format(self.get_setting("USER_LOOKUP_API"))
        #return False
        return "{}".format(self.get_setting("USER_LOOKUP_API"))

    @property
    def unloanable_suffix(self):
        return self.get_setting("UNLOANABLE_SUFFIX")

    # Custom Panels
    STOCK_ITEM_LOAN_PANEL_TITLE = "Loaning"

    
    def get_panel_context(self, view, request, context):
        """Returns enriched context."""
        ctx = super().get_panel_context(view, request, context)

        ctx['perm'] = check_user_role(request.user,self.ROLE,"view")
        if isinstance(view, StockItemDetail):
             ctx['stock_labonly'] = is_stock_labonly(stock_pk=ctx['item'].pk)
             ctx['stock_avail'] = is_stock_available(stock_pk=ctx['item'].pk)
        if isinstance(view, PartDetail):
            (ctx['part_avail'],ctx['part_loaned'],ctx['part_labonly']) = get_part_availability(part_pk=ctx['part'].pk)
        return ctx

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
        if isinstance(view, PartDetail):
            panels.append({
                "title": LoanPlugin.STOCK_ITEM_LOAN_PANEL_TITLE,
                "icon": "fas fa-handshake",
                "content_template": "part_loan_panel.html",
                "javascript_template": "",
                "role": LoanPlugin.ROLE,
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



    def check_late(self,*args,**kwargs):
        send_email("Testing email transmit","Server is able to send e-mail!",["wiltk2@rpi.edu"])
        if not self.get_setting('ENABLE_OVERDUE_EMAIL'):
            return False 
        overdue_list = LoanSession.objects.filter(LoanSession.OVERDUE_FILTER)
        for oloan in overdue_list:
            send_notice = True
            if oloan.notices_sent:
                since_last_notice = date.today() - oloan.last_notice
                if since_last_notice.days < self.get_setting('OVERDUE_NOTICE_FREQ'):
                    send_notice = False
            if send_notice == True:
                oloan.notices_sent += 1
                oloan.last_notice = date.today()
                oloan.save()
                send_email(
                    'ECSE Stockroom/Mercer XLab Overdue Loan Notice. Notice Number: {}'.format(oloan.notices_sent),
                    'Hello, \n You are receiving this e-mail because our records indicate that you have an overdue loan for hardware lent through either the Mercer XLab or the ECSE Stockroom. There hardware is as follows:\n\nItem: {}\nSerial Number: {}\nDate Loaned: {}\nDue Date: {}\n\nPlease return these items in a timely manner. You may return them to Chris Rinaldi (JEC6009) or the Mercer XLab Entry Desk (JEC 6th Floor).\n\nSend to: {}'.format(oloan.stock.part.full_name,oloan.stock.serial,oloan.loan_date,oloan.due_date,oloan.loan_user.email),
                    ['wiltk2@rpi.edu']
                )
                    
        return len(overdue_list)

# Additional functions
def is_stock_labonly(stockitem="",stock_pk=""):
    # Check to see if labonly designation exists
    if not LoanPlugin().unloanable_suffix: # I feel like this is a bad way to get the unloanable_suffix, but can't think of a better way
        return False
    # Get stockitem if given pk
    if not stockitem:
        stockitem = StockItem.objects.filter(pk=stock_pk)
        if not stockitem:
            return False
        stockitem = stockitem[0]
    # Check if item is marked Lab Only
    if stockitem.serial.endswith(LoanPlugin().unloanable_suffix):
        return True
    # Item exists and is not lab only
    return False

def is_stock_available(stockitem="",stock_pk=""):
    # Check if stock item actually exists
    if not stockitem:
        if not StockItem.objects.filter(pk=stock_pk):
            return False
    else:
        stock_pk = stockitem.pk
    # Check to see if it is currently loaned
    if LoanSession.objects.filter(stock=stock_pk,returned=False):
        return False
    # Item exists and isn't loaned
    return True

def get_part_availability(part="",part_pk=""):
    """ Returns a tuple of part availability, containing:
        1. Number of parts available to loan
        2. Number of parts currently on loan
        3. Number of parts designated lab only
    """
    # Get part if given pk
    if not part:
        part = Part.objects.filter(pk=part_pk)
        if not part:
            return False
        part = part[0]
    # Get list of stock for part
    partstock = part.stock_entries()
    # tracking numbers
    Navail = len(partstock) # Assume all parts are available to loan to start
    Nloaned = 0 # Assume none are loaned to start
    Nlabonly = 0 # Assume none are lab only to start
    # Loop through each stock item
    for stock in partstock:
        if is_stock_labonly(stockitem=stock):
            Nlabonly += 1
            Navail -= 1
        elif not is_stock_available(stockitem=stock):
            Navail -= 1
            Nloaned += 1
    return (Navail,Nloaned,Nlabonly)
