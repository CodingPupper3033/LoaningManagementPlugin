import datetime

from django.urls import re_path, path, include
from rest_framework import permissions

from InvenTree.mixins import (ListCreateAPI, RetrieveUpdateDestroyAPI)
from .models import (LoanSession, LoanUser)
from .serializers import (LoanSessionSerializer, LoanUserSerializer)


class LoanSessionMixin:
    """Mixin class for LoanSession API endpoints"""
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()

    permission_classes = [permissions.IsAuthenticated]


class LoanSessionList(LoanSessionMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance"""

    def get_queryset(self, *args, **kwargs):
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

    permission_classes = [permissions.IsAuthenticated]


class LoanUserList(LoanUserMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanUser objects, or creating a new LoanUser instance"""
    pass


class LoanUserDetail(LoanUserMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanUser object."""
    pass


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
