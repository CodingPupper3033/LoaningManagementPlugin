import datetime

from rest_framework import serializers
# from .loanmanagement import LoaningManagementPlugin


def getDefaultDueDate():
    return datetime.date.today()
    # + datetime.timedelta(
    #     days=int(LoaningManagementPlugin().get_setting("DEFAULT_LOAN_DURATION_DAYS", cache=False)))


class LoanSessionSerializer(serializers.ModelSerializer):
    loan_date = serializers.DateField(default=datetime.date.today, initial=datetime.date.today)
    due_date = serializers.DateField(default=getDefaultDueDate, initial=getDefaultDueDate)

    class Meta:
        from .models import LoanSession
        app_label = "loanmanagement"
        fields = ('id', 'stock_item', 'quantity', 'loan_date', 'due_date')
        model = LoanSession
