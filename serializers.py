import datetime

from rest_framework import serializers

from .loanmanagement import LoaningManagementPlugin


def get_default_due_date():
    """Adds the default loan time to the current day"""
    return datetime.date.today() + datetime.timedelta(
        days=int(LoaningManagementPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


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
        app_label = "loanmanagement"
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
        app_label = "loanmanagement"
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
        app_label = "loanmanagement"
        fields = (
            'pk', 'stock', 'quantity', 'loan_date', 'due_date', 'returned', 'returned_date', 'loan_user',
            'location', 'stock_detail', 'loan_user_detail')
        model = LoanSession
