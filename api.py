import django_filters
from django.urls import re_path, path, include
from rest_framework import permissions
from django_filters import rest_framework as rest_filters

from InvenTree.mixins import (ListCreateAPI, RetrieveUpdateDestroyAPI)
from InvenTree.api import APIDownloadMixin, ListCreateDestroyAPIView
from .models import (LoanSession, LoanUser)
from .serializers import (LoanSessionSerializer, LoanUserSerializer)

from InvenTree.filters import (SEARCH_ORDER_FILTER_ALIAS)
from InvenTree.helpers import str2bool


class LoanSessionFilter(django_filters.FilterSet):
    """
    Allow filtering LoanSessions by:
        overdue: session is past due and not returned
        current: session is currently loaned and not overdue
        returned: session has been returned
        quantity: quantity of items in the session - NOT TESTED
    """

    class Meta:
        model = LoanSession  # Django model to filter for

        fields = ['quantity']  # Searchable by quantity

    # Loan Session 'State' filters
    overdue = rest_filters.BooleanFilter(label='Overdue', method='filter_overdue')

    # noinspection PyUnusedLocal
    @staticmethod
    def filter_overdue(queryset, name, value):
        """Is the session is overdue"""
        if str2bool(value):
            return queryset.filter(LoanSession.OVERDUE_FILTER).order_by('due_date')
        else:
            return queryset.exclude(LoanSession.OVERDUE_FILTER).order_by('due_date')

    current = rest_filters.BooleanFilter(label='current', method='filter_current')

    # noinspection PyUnusedLocal
    @staticmethod
    def filter_current(queryset, name, value):
        """Is the session currently loaned and not overdue."""
        if str2bool(value):
            return queryset.filter(LoanSession.CURRENT_FILTER).order_by('due_date')
        else:
            return queryset.exclude(LoanSession.CURRENT_FILTER).order_by('due_date')

    returned = rest_filters.BooleanFilter(label='returned')


class LoanSessionMixin:
    """
    Mixin class for LoanSession API endpoints
    Every API endpoint for LoanSession objects should inherit from this class
    """
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()

    permission_classes = [permissions.IsAuthenticated]  # TODO: Only work with proper permissions (and test)


class LoanSessionList(LoanSessionMixin, APIDownloadMixin, ListCreateAPI):
    """
    API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance
    """
    filterset_class = LoanSessionFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    def download_queryset(self, queryset, export_format):
        # TODO - Implement this
        raise NotImplementedError("Implement sometime maybe so we can download the table")


class LoanSessionDetail(LoanSessionMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanSession object."""
    pass


class LoanUserFilter(django_filters.FilterSet):
    """
    LoanSession object filter
    Allow filtering LoanSessions by:
        active: is the user active/still part of the organization (not archived)
        restricted: is the user restricted/temporarily banned from loaning items
    """

    class Meta:
        model = LoanUser

        fields = ['active', 'restricted']


class LoanUserMixin:
    """
    Mixin class for LoanSession API endpoints
    Every API endpoint for LoanUser objects should inherit from this class
    """
    serializer_class = LoanUserSerializer
    queryset = LoanUser.objects.all()


class LoanUserList(LoanUserMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanUser objects, or creating a new LoanUser instance"""
    filterset_class = LoanUserFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    # What to search for when searching for a LoanUser (in a table or using the search parameter)
    search_fields = [
        'first_name',
        'last_name',
        'email',
        '=idn'  # Search for ID number, but has to be exact
    ]

    # Parameters to order the queryset/API requests by
    ordering = [
        '-active',  # Active users first
        'restricted',  # Unrestricted users first
        'last_name',  # Alphabetical by last name
        'first_name',  # Alphabetical by first name
        'email'
    ]


class LoanUserDetail(LoanUserMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanUser object."""
    pass


# URLS for the API endpoints
loan_session_api_urls = [
    path(r'<int:pk>/', include([
        re_path(r'^.*$', LoanSessionDetail.as_view(), name='api-loan-session-detail')
    ])),
    re_path(r'^.*$', LoanSessionList.as_view(), name='api-loan-session-list'),
]

loan_user_api_urls = [
    path(r'<int:pk>/', include([
        re_path(r'^.*$', LoanUserDetail.as_view(), name='api-loan-user-detail')
    ])),
    re_path(r'^.*$', LoanUserList.as_view(), name='api-loan-user-list'),
]
