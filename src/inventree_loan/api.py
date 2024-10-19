import django_filters
from django.urls import re_path, path, include
from rest_framework import permissions
from django_filters import rest_framework as rest_filters
from django.contrib.auth import get_user_model

from InvenTree.mixins import (CreateAPI, ListCreateAPI, RetrieveUpdateDestroyAPI)
#from InvenTree.api import APIDownloadMixin, ListCreateDestroyAPIView
from InvenTree.api import ListCreateDestroyAPIView
from .models import LoanSession
from .serializers import (LoanSessionSerializer, LoanUserSerializer, LoanSessionReturnSerializer, LoaneeSerializer)

from InvenTree.filters import (SEARCH_ORDER_FILTER_ALIAS)
from InvenTree.helpers import str2bool


class LoanSessionFilter(django_filters.FilterSet):
    """
    Allow filtering LoanSessions by:
        email: sessions by user email
        overdue: session is past due and not returned
        current: session is currently loaned and not overdue
        returned: session has been returned
        quantity: quantity of items in the session - NOT TESTED
    """

    class Meta:
        model = LoanSession  # Django model to filter for

        fields = ['quantity', 'stock','loan_user__id']#,a'loan_user__email']

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

    email = rest_filters.CharFilter(label='E-mail',field_name='loan_user__email',lookup_expr='iexact')


class LoanSessionMixin:
    """
    Mixin class for LoanSession API endpoints
    Every API endpoint for LoanSession objects should inherit from this class
    """
    serializer_class = LoanSessionSerializer
    queryset = LoanSession.objects.all()

    permission_classes = [permissions.IsAuthenticated]  # TODO: Only work with proper permissions (and test)


class LoanSessionList(LoanSessionMixin, ListCreateAPI):
    """
    API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance
    """
    filterset_class = LoanSessionFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    def download_queryset(self, queryset, export_format):
        # TODO - Implement this
        raise NotImplementedError("Implement sometime maybe so we can download the table")

    def get_serializer(self, *args, **kwargs):
        try:
            params = self.request.query_params

            for key in ['stock_detail', 'user_detail']:
                kwargs[key] = str2bool(params.get(key, False))
        except AttributeError:
            pass

        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)


class LoanSessionStockItem(LoanSessionMixin, ListCreateAPI):
    """
    API endpoint for accessing a list of LoanSession objects, or creating a new LoanSession instance
    """
    filterset_class = LoanSessionFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS
    lookup_field="stock"

    def download_queryset(self, queryset, export_format):
        # TODO - Implement this
        raise NotImplementedError("Implement sometime maybe so we can download the table")

    def get_serializer(self, *args, **kwargs):
        try:
            params = self.request.query_params

            for key in ['stock_detail', 'user_detail']:
                kwargs[key] = str2bool(params.get(key, False))
        except AttributeError:
            pass

        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

class LoanSessionDetail(LoanSessionMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanSession object."""
    def get_serializer(self, *args, **kwargs):
        try:
            params = self.request.query_params

            for key in ['stock_detail', 'user_detail']:
                kwargs[key] = str2bool(params.get(key, False))
        except AttributeError:
            pass

        kwargs['context'] = self.get_serializer_context()

        return self.serializer_class(*args, **kwargs)

#class LoanSessionStockItem(LoanSessionMixin, RetrieveUpdateDestroyAPI):
#    """API endpoint for detail view of all LoanSession objects for a single Stock Item."""
#    lookup_field="stock"
#    pass

class LoanSessionAdjustView(CreateAPI):
    """A generic class for handling loan session actions.

    Subclasses exist for:

    - StockCount: count stock items
    """

    queryset = LoanSession.objects.none()


class LoanSessionReturn(LoanSessionAdjustView):
    """API endpoint for returning a loaned item."""

    serializer_class = LoanSessionReturnSerializer


class LoanUserFilter(django_filters.FilterSet):
    """
    LoanSession object filter
    Allow filtering LoanSessions by:
        active: is the user active/still part of the organization (not archived)
        restricted: is the user restricted/temporarily banned from loaning items
    """

    class Meta:
        model = get_user_model()

        fields = "__all__"
        #fields = ['active', 'restricted']


class LoanUserMixin:
    """
    Mixin class for LoanSession API endpoints
    Every API endpoint for LoanUser objects should inherit from this class
    """
    serializer_class = LoanUserSerializer
    queryset = get_user_model().objects.all()


class LoanUserList(LoanUserMixin, ListCreateAPI):
    """API endpoint for accessing a list of LoanUser objects, or creating a new LoanUser instance"""
    filterset_class = LoanUserFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    # What to search for when searching for a LoanUser (in a table or using the search parameter)
    search_fields = [
        'pk',
        'first_name',
        'last_name',
        'email',
        'username',
    ]

    # Parameters to order the queryset/API requests by
    ordering = [
        'last_name',  # Alphabetical by last name
        'first_name',  # Alphabetical by first name
        'email'
    ]


class LoanUserDetail(LoanUserMixin, RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LoanUser object."""
    pass

class LoaneeFilter(django_filters.FilterSet):
    """
    Allow filtering Loanees by:
        ????
    """

    class Meta:
        model = get_user_model()  # Django model to filter for

        fields = '__all__'

class LoaneeMixin:
    """
    Mixin class for Loanee API endpoints
    Every API endpoint for Loanee objects should inherit from this class
    """
    serializer_class = LoaneeSerializer
    queryset = get_user_model().objects.all()

class LoaneeList(LoaneeMixin, ListCreateAPI):
    """
    API endpoint for accessing a list of Loanees
    """
    filterset_class = LoaneeFilter
    filter_backends = SEARCH_ORDER_FILTER_ALIAS

    def download_queryset(self, queryset, export_format):
        # TODO - Implement this
        raise NotImplementedError("Implement sometime maybe so we can download the table")

    def get_queryset(self, *args, **kwargs):
        """Get the number of items per user"""
        queryset = super().get_queryset(*args, **kwargs)
        queryset = LoaneeSerializer.annotate_queryset(queryset)
        return queryset

    search_fields = [
        'pk',
        'first_name',
        'last_name',
        'email',
        'username',
    ]

    ordering_fields = [
        'last_name',
        'first_name',
        'email',
        'loaned',
        'overdue',
        'returned',
    ]

    ordering = ['email']

# URLS for the API endpoints
loan_session_api_urls = [
    path(r'<int:pk>/', include([
        re_path(r'^.*$', LoanSessionDetail.as_view(), name='api-loan-session-detail')
    ])),
    path(r'stock/<int:stock>/', include([
        re_path(r'^.*$', LoanSessionStockItem.as_view(), name='api-loan-session-stockitem')
    ])),
    re_path(r'^return/', LoanSessionReturn.as_view(), name='api-loan-session-return'),
    re_path(r'^.*$', LoanSessionList.as_view(), name='api-loan-session-list'),
]

loan_user_api_urls = [
    path(r'<int:pk>/', include([
        re_path(r'^.*$', LoanUserDetail.as_view(), name='api-loan-user-detail')
    ])),
    re_path(r'^.*$', LoanUserList.as_view(), name='api-loan-user-list'),
]

loanee_api_urls = [
    re_path(r'^.*$', LoaneeList.as_view(), name='api-loanee-list'),
]
