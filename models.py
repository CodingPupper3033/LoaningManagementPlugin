import datetime

from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import models


class LoanUser(models.Model):
    class Meta:
        app_label = "loanmanagement"

    id = models.AutoField(  # Internal ID value
        primary_key=True,
        verbose_name=_('Id')
    )

    first_name = models.CharField(  # User's First Name
        max_length=250,
        verbose_name=_('Name')
    )

    last_name = models.CharField(  # User's Last Name
        max_length=250,
        verbose_name=_('Name')
    )

    email = models.EmailField(  # User's Email
        max_length=20,
        verbose_name=_('Email')
    )

    idn = models.IntegerField(  # User's ID Number (For RPI, it's RIN)
        verbose_name=_('RIN')
    )

    active = models.BooleanField(  # Is this user still active (and allowed to loan items)
        verbose_name=_('Active'),
        default=True
    )

    restricted = models.BooleanField(  # Is this user able to loan items?
        verbose_name=_('Restricted'),
        default=False
    )


class LoanSession(models.Model):
    class Meta:
        app_label = "loanmanagement"

    id = models.AutoField(
        primary_key=True,
        verbose_name=_('Id')
    )

    stock_item = models.ForeignKey(
        "stock.StockItem",
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        verbose_name=_("Stock Quantity"),
        max_digits=15, decimal_places=5, validators=[MinValueValidator(0)],
        default=1
    )

    loan_date = models.DateField(
        verbose_name=_('Date Loaned')
    )

    due_date = models.DateField(
        verbose_name=_('Due Date')
    )

    returned = models.BooleanField(
        default=False,
        verbose_name=_("Returned")
    )

    date_returned = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Due Date')
    )

    loan_user = models.ForeignKey(
        "loanmanagement.LoanUser",
        on_delete=models.CASCADE
    )

    location = models.CharField(
        max_length=250,
        verbose_name=_('Location'),
        null=True,
        blank=True
    )
