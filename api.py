from django.urls import re_path, path, include

from InvenTree.mixins import (ListCreateAPI, RetrieveUpdateDestroyAPI)
from .models import (LoanSession)
from .serializers import (LoanSessionSerializer)


class LoanSessionMixin:
    """Mixin class for LoanSession API endpoints"""
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()


class LoanSessionList(LoanSessionMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance"""
    pass


class LoanSessionDetail(LoanSessionMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanSession object."""
    pass


loan_session_api_urls = [
    # path(r'<int:pk>/', include([
    #     re_path(r'^.*$', LoanSessionDetail.as_view(), name='api-part-detail')
    # ])),
    # re_path(r'^.*$', LoanSessionList.as_view(), name='api-loan-session-list'),
]
