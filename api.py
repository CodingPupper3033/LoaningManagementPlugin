import datetime

import django_filters
from django.urls import re_path, path, include
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as rest_filters

from InvenTree.mixins import (ListCreateAPI, RetrieveUpdateDestroyAPI)
from InvenTree.api import APIDownloadMixin, ListCreateDestroyAPIView
from .models import (LoanSession, LoanUser)
from .serializers import (LoanSessionSerializer, LoanUserSerializer)

from InvenTree.filters import (ORDER_FILTER, SEARCH_ORDER_FILTER,
                               SEARCH_ORDER_FILTER_ALIAS)
from InvenTree.helpers import str2bool


class LoanSessionFilter(django_filters.FilterSet):
    """LoanSession object filter"""

    class Meta:
        model = LoanSession

        fields = ['quantity']

    overdue = rest_filters.BooleanFilter(label='Overdue', method='filter_overdue')

    def filter_overdue(self, queryset, name, value):
        """Filter by if session is overdue."""
        if str2bool(value):
            return queryset.filter(LoanSession.OVERDUE_FILTER).order_by('due_date')
        else:
            return queryset.exclude(LoanSession.OVERDUE_FILTER).order_by('due_date')

    current = rest_filters.BooleanFilter(label='current', method='filter_current')

    def filter_current(self, queryset, name, value):
        """Filter by if session is currently loaned and not overdue."""
        if str2bool(value):
            return queryset.filter(LoanSession.CURRENT_FILTER).order_by('due_date')
        else:
            return queryset.exclude(LoanSession.CURRENT_FILTER).order_by('due_date')

    returned = rest_filters.BooleanFilter(label='returned')


class LoanSessionMixin:
    """Mixin class for LoanSession API endpoints"""
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()

    permission_classes = [permissions.IsAuthenticated]


class LoanSessionList(LoanSessionMixin, APIDownloadMixin, ListCreateDestroyAPIView):
    """API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance"""
    filterset_class = LoanSessionFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    def download_queryset(self, queryset, export_format):
        raise NotImplementedError("Implement sometime maybe so we can download the table")


class LoanSessionDetail(LoanSessionMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanSession object."""
    pass


class LoanUserMixin:
    """Mixin class for LoanSession API endpoints"""
    serializer_class = LoanUserSerializer
    queryset = LoanUser.objects.all()


class LoanUserList(LoanUserMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanUser objects, or creating a new LoanUser instance"""
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    search_fields = [
        'first_name',
        'last_name',
        'email',
        '=idn'
    ]

    ordering = [
        'last_name',
        'first_name',
        'email'
    ]


class LoanUserDetail(LoanUserMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanUser object."""
    pass


# URLS for the API

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
