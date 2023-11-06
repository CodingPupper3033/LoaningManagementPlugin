import datetime

from django import forms

class LoanSessionMaker(forms.Form):
    class Meta:
        app_label = "loanmanagement"

    stock_item = forms.IntegerField(initial=1)
    quantity = forms.DecimalField(initial=1.0)
    loan_date = forms.DateField(initial=datetime.datetime.now())
    due_date = forms.DateField(initial=datetime.datetime.now() + datetime.timedelta(days=10))


