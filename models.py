import datetime

from django.core.validators import MinValueValidator
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models


class LoanUser(models.Model):
    #from .loanmanagement import LoaningManagementPlugin
    @staticmethod
    def get_api_url():
        """Return API url."""
        return '/plugin/loan/api/loanuser/'

    class Meta:
        app_label = "loanmanagement"

    first_name = models.CharField(  # User's First Name
        max_length=250,
        verbose_name=_('First Name'),
        null=False,
        blank=False,
        default=None
    )

    last_name = models.CharField(  # User's Last Name
        max_length=250,
        verbose_name=_('Last Name'),
        null=False,
        blank=False,
        default=None
    )

    email = models.EmailField(  # User's Email
        max_length=20,
        verbose_name=_('Email'),
        null=False,
        blank=False,
        default=None
    )

    idn = models.IntegerField(  # User's ID Number (For RPI, it's RIN)
        verbose_name=_('RIN'),
        unique=True,
        null=False,
        blank=False
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
    @staticmethod
    def get_api_url():
        """Return API url."""
        return '/plugin/loan/api/loansession/'

    class Meta:
        app_label = "loanmanagement"

    # Can a session be considered "overdue"?
    OVERDUE_FILTER = Q(
        returned=False,
        due_date__lt=datetime.date.today()
    )

    # Can a session be considered "outstanding"?
    CURRENT_FILTER = Q(
        returned=False,
        due_date__gte=datetime.date.today(),
        loan_date__lte=datetime.date.today()
    )

    stock = models.ForeignKey(
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

    returned_date = models.DateField(
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
