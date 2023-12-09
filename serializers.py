import datetime

from rest_framework import serializers

from .loanmanagement import LoaningManagementPlugin


def get_default_due_date():
    """Adds the default loan time to the current day"""
    return datetime.date.today() + datetime.timedelta(
        days=int(LoaningManagementPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


def get_overdue_sessions_count():
    """Returns a count of all overdue sessions"""
    from .models import LoanSession
    overdue = LoanSession.objects.filter(LoanSession.OVERDUE_FILTER)
    overdue_serializer = LoanSessionSerializer(overdue, many=True)
    return len(overdue_serializer.data)


class LoanUserSerializer(serializers.ModelSerializer):
    """Serializer for loan users"""

    # The username will be the same as the email. This is so that a loan user can be rendered the same as an InvenTree user in forms.
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.email

    class Meta:
        from .models import LoanUser
        app_label = "loanmanagement"
        fields = ('pk', 'first_name', 'last_name', 'email', 'active', 'restricted', 'username')
        model = LoanUser


class LoanUserBriefSerializer(serializers.ModelSerializer):
    """Serializer for loan users"""

    # The username will be the same as the email. This is so that a loan user can be rendered the same as an InvenTree user in forms.
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.email

    class Meta:
        from .models import LoanUser
        app_label = "loanmanagement"
        fields = ('pk', 'first_name', 'last_name', 'email', 'username')
        model = LoanUser


class LoanSessionSerializer(serializers.ModelSerializer):
    """Serializer for loan sessions"""

    # The default day the item was loaned will be set to today.
    loan_date = serializers.DateField(default=datetime.date.today, initial=datetime.date.today)
    # The default day the item will be expected to be returned will be today+the default time
    due_date = serializers.DateField(default=get_default_due_date, initial=get_default_due_date)

    # The stock item will be serialized with the stock item serializer. This also shows the part detail.
    from stock.serializers import StockItemSerializer
    stock_detail = StockItemSerializer(source='stock', many=False, read_only=True, part_detail=True)

    loan_user_detail = LoanUserBriefSerializer(source='loan_user', many=False, read_only=True)

    class Meta:
        from .models import LoanSession
        app_label = "loanmanagement"
        fields = (
            'pk', 'stock', 'quantity', 'loan_date', 'due_date', 'returned', 'returned_date', 'loan_user',
            'location', 'stock_detail', 'loan_user_detail')
        model = LoanSession
