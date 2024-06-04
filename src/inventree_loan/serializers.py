import datetime

from rest_framework import serializers

from .LoanPlugin import LoanPlugin
from django.utils.translation import gettext_lazy as _
from django.db import transaction


def get_default_due_date():
    """Adds the default loan time to the current day"""
    return datetime.date.today() + datetime.timedelta(
        days=int(LoanPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


class LoanUserSerializer(serializers.ModelSerializer):
    """Serialize Loan Users"""

    # The username will be the same as the email. This is so that a loan user can be rendered as an InvenTree user in modals.
    username = serializers.SerializerMethodField()

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
        from .models import LoanUser
#        app_label = "LoanPlugin"
        fields = ('pk', 'first_name', 'last_name', 'email', 'active', 'restricted', 'username', 'idn')
        extra_kwargs = {'idn': {'write_only': True}}
        model = LoanUser


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
    username = serializers.SerializerMethodField()

    @staticmethod
    def get_username(obj):
        return obj.email

    class Meta:
        from .models import LoanUser
#        app_label = "LoanPlugin"
        fields = ('pk', 'first_name', 'last_name', 'email', 'username')
        model = LoanUser


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

    # TODO: Add a validator that checks that there is enough of the stock to loan out, not just was it already loaned out
    @staticmethod
    def validate_stock(value):
        """Validate that the stock item is not already loaned out."""
        from .models import LoanSession
        if LoanSession.objects.filter(stock=value, returned=False).exists():
            raise serializers.ValidationError("Stock item is already loaned out")
        return value

    class Meta:
        from .models import LoanSession
#        app_label = "LoanPlugin"
        fields = (
            'pk', 'stock', 'quantity', 'loan_date', 'due_date', 'returned', 'returned_date', 'loan_user',
            'location', 'stock_detail', 'loan_user_detail')
        model = LoanSession

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        stock_detail = kwargs.pop('stock_detail', False)
        user_detail = kwargs.pop('user_detail', False)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if not stock_detail:
            self.fields.pop('stock_detail')

        if not user_detail:
            self.fields.pop('loan_user_detail')


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
