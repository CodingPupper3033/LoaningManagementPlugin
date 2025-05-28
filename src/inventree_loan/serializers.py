import datetime

from rest_framework import serializers

from .LoanPlugin import LoanPlugin,is_stock_labonly
from django.utils.translation import gettext_lazy as _
from django.db import transaction

# For the loan annotations
from django.db.models import F, Func, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce
from sql_util.utils import SubqueryCount
from .models import LoanSession

import logging
logger = logging.getLogger('inventree')

def get_default_due_date():
    """Adds the default loan time to the current day"""
    return datetime.date.today() + datetime.timedelta(
        days=int(LoanPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


class LoanUserSerializer(serializers.ModelSerializer):
    """Serialize Loan Users"""

    # The username will be the same as the email. This is so that a loan user can be rendered as an InvenTree user in modals.
    # username = serializers.SerializerMethodField()

    @staticmethod
    def get_username(obj):
        return obj.email

    def validate(self, data):
        """Validate the data being passed in."""

        # If the user is not active, they should be restricted.
        if 'active' in data.values() and not data['active']:
            data['restricted'] = True

        return data

    class Meta:
        from django.contrib.auth import get_user_model
#        app_label = "LoanPlugin"
        fields = ('pk', 'first_name', 'last_name', 'email', 'username',)
        model = get_user_model()


class LoanUserBriefSerializer(serializers.ModelSerializer):
    """
    Brief Serializer for loan users. This is used in the loan session serializer.
    Serializes:
        pk
        first_name
        last_name
        email
        username
    """

    # The username will be the same as the email. This is so that a loan user can be rendered the same as an InvenTree user in forms.
    # username = serializers.SerializerMethodField()

    @staticmethod
    def get_username(obj):
        return obj.email

    class Meta:
        from django.contrib.auth import get_user_model
#        app_label = "LoanPlugin"
        fields = ('pk', 'first_name', 'last_name', 'email', 'username')
        model = get_user_model()


class LoanSessionSerializer(serializers.ModelSerializer):
    """Serializes Loan Sessions"""

    # The default day the item was loaned will be set to today.
    loan_date = serializers.DateField(default=datetime.date.today, initial=datetime.date.today)
    # The default day the item will be expected to be returned will be today+the default time
    due_date = serializers.DateField(default=get_default_due_date, initial=get_default_due_date)

    # The stock item will be serialized with the stock item serializer. This also shows the part detail.
    from stock.serializers import StockItemSerializer
    stock_detail = StockItemSerializer(source='stock', many=False, read_only=True, part_detail=True)

    loan_user_detail = LoanUserBriefSerializer(source='loan_user', many=False, read_only=True)
    loaner_detail = LoanUserBriefSerializer(source='loaner', many=False, read_only=True)

    # TODO: Add a validator that checks that there is enough of the stock to loan out, not just was it already loaned out
    @staticmethod
    def validate_stock(value):
        """Validate that the stock item is not already loaned out."""
        from .models import LoanSession
        if LoanSession.objects.filter(stock=value, returned=False).exists():
            raise serializers.ValidationError("Stock item is already loaned out")
        if is_stock_labonly(stockitem=value):
            raise serializers.ValidationError("Selected item is designated Lab Only")
        return value

    class Meta:
        from .models import LoanSession
#        app_label = "LoanPlugin"
        fields = (
            'pk', 'stock', 'quantity', 'loan_date', 'due_date', 'returned', 'returned_date', 'loan_user',
            'location', 'stock_detail', 'loan_user_detail','loaner','loaner_detail')
        model = LoanSession

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        stock_detail = kwargs.pop('stock_detail', False)
        user_detail = kwargs.pop('user_detail', False)
        loaner_detail = kwargs.pop('loaner_detail', False)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if not stock_detail:
            self.fields.pop('stock_detail')

        if not user_detail:
            self.fields.pop('loan_user_detail')

        if not loaner_detail:
            self.fields.pop('loaner_detail')


class LoanSessionReturnItemSerializer(serializers.Serializer):
    """Serializer for a single LoanSession within a loan session return request.

    Fields:
        - item: LoanSession object
        - returned_date: Date to record as returned
    """
    class Meta:
#        app_label = "LoanPlugin"
        fields = ['pk', 'returned_date']

    from .models import LoanSession
    pk = serializers.PrimaryKeyRelatedField(
        queryset=LoanSession.objects.all(),
        many=False,
        allow_null=False,
        required=True,
        label='loan_session',
        help_text=_('LoanSession primary key value')
    )

    returned_date = serializers.DateField(
        allow_null=False,
        required=True,
        label='returned_date',
        help_text=_('Date the item was returned')
    )


class LoanSessionReturnSerializer(serializers.Serializer):
    """Serializer for returning loansession item(s)."""

    items = LoanSessionReturnItemSerializer(many=True)

    class Meta:
#        app_label = "LoanPlugin"
        fields = ['items']

    def save(self):
        data = self.validated_data

        items = data['items']

        with transaction.atomic():
            for item in items:
                loan_session = item['pk']

                loan_session.return_item(
                    returned_date=item['returned_date']
                )

class LoaneeSerializer(serializers.ModelSerializer):
    """Serializer for loanee objects."""
    # The username will be the same as the email. This is so that a loan user can be rendered as an InvenTree user in modals.
    username = serializers.SerializerMethodField()

    loaned = serializers.IntegerField(read_only=True, label=_('Loaned'))
    overdue = serializers.IntegerField(read_only=True, label=_('Overdue'))
    returned = serializers.IntegerField(read_only=True, label=_('Returned'))
    total = serializers.IntegerField(read_only=True, label=_('Total'))

    class Meta:
        from django.contrib.auth import get_user_model
        fields = ('pk', 'first_name', 'last_name', 'email', 'username','loaned','overdue','returned','total')
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)
        
    @staticmethod
    def get_username(obj):
        return obj.email

    @staticmethod
    def annotate_queryset(queryset):
        """Annotate the items loaned into the queryset."""
        queryset = queryset.annotate(
            loaned= annotate_loanee_items(status='current'),
            overdue= annotate_loanee_items(status='overdue'),
            returned= annotate_loanee_items(status='returned'),
            total=annotate_loanee_items()
        )
        queryset = queryset.exclude(total=0)
        return queryset
        



""" This are based on annotate_location_items() from stock/filters.py """
def annotate_loanee_items(status=None):
    """Construct a queryset annotation which returns the number of loaned utems to a particular user."""

    # Construct a subquery to provide all items loaned by a specific user
    if status == 'overdue':
        subquery = LoanSession.objects.all().filter(
            LoanSession.OVERDUE_FILTER,
            loan_user=OuterRef('pk')
        )
    elif status == 'current':
        subquery = LoanSession.objects.all().filter(
            LoanSession.CURRENT_FILTER,
            loan_user=OuterRef('pk')
        )
    elif status == 'returned':
        subquery = LoanSession.objects.all().filter(
            LoanSession.RETURNED_FILTER,
            loan_user=OuterRef('pk')
        )
    else: #total
        subquery = LoanSession.objects.all().filter(
            loan_user=OuterRef('pk')
        )

    

    return Coalesce(
        Subquery(
            subquery.annotate(total=Func(F('pk'), function='COUNT', output_field=IntegerField()))
            .values('total')
            .order_by()
        ),
        0,
        output_field=IntegerField(),
    )
