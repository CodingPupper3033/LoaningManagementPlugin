import datetime

from django.urls import re_path, path, include
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as rest_filters

from InvenTree.mixins import (ListCreateAPI, RetrieveUpdateDestroyAPI)
from .models import (LoanSession, LoanUser)
from .serializers import (LoanSessionSerializer, LoanUserSerializer)

from InvenTree.filters import (ORDER_FILTER, SEARCH_ORDER_FILTER,
                               SEARCH_ORDER_FILTER_ALIAS)


class LoanSessionMixin:
    """Mixin class for LoanSession API endpoints"""
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()

    permission_classes = [permissions.IsAuthenticated]


class LoanSessionList(LoanSessionMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance"""

    def get_queryset(self, *args, **kwargs):
        """Gets the queryset."""
        # TODO FILTERSET?
        queryset = super().get_queryset(*args, **kwargs)

        overdue = self.request.query_params.get('overdue')
        if overdue is not None and overdue.lower() == 'true':
            return queryset.filter(returned=False, due_date__lt=datetime.date.today()).order_by('due_date')
        return queryset


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
