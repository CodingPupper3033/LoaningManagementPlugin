import datetime

from rest_framework import serializers

from .loanmanagement import LoaningManagementPlugin


def get_default_due_date():
    """Adds the default loan time to the current day"""
    return datetime.date.today() + datetime.timedelta(
        days=int(LoaningManagementPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


class LoanSessionSerializer(serializers.ModelSerializer):
    """Serializer for loan sessions"""

    # The default day the item was loaned will be set to today.
    loan_date = serializers.DateField(default=datetime.date.today, initial=datetime.date.today)
    # The default day the item will be expected to be returned will be today+the default time
    due_date = serializers.DateField(default=get_default_due_date, initial=get_default_due_date)

    # The stock item will be serialized with the stock item serializer. This also shows the part detail.
    from stock.serializers import StockItemSerializer
    stock_detail = StockItemSerializer(source='stock', many=False, read_only=True, part_detail=True)

    class Meta:
        from .models import LoanSession
        app_label = "loanmanagement"
        fields = (
            'id', 'stock', 'quantity', 'loan_date', 'due_date', 'returned', 'date_returned', 'loan_user',
            'location', 'stock_detail')
        model = LoanSession


class LoanUserSerializer(serializers.ModelSerializer):
    """Serializer for loan users"""

    class Meta:
        from .models import LoanUser
        app_label = "loanmanagement"
        fields = ('id', 'first_name', 'last_name', 'email', 'idn', 'active', 'restricted')
        model = LoanUser
