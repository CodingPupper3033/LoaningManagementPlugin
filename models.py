import datetime

from django.core.validators import MinValueValidator
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models


class LoanUser(models.Model):
    """
    Model for a user that can loan items.
    This is a separate model from the InvenTree user model so that loan users can be created without creating an
    InvenTree user (without them logging in).
    """
    @staticmethod
    def get_api_url():
        """Return API url."""
        return '/plugin/loan/api/loanuser/'

    class Meta:
        app_label = "loanmanagement"

    first_name = models.CharField(
        max_length=250,
        verbose_name=_('First Name'),
        null=False,
        blank=False,
        default=None
    )

    last_name = models.CharField(
        max_length=250,
        verbose_name=_('Last Name'),
        null=False,
        blank=False,
        default=None
    )

    email = models.EmailField(
        max_length=20,
        verbose_name=_('Email'),
        unique=True,
        null=False,
        blank=False,
        default=None
    )

    idn = models.IntegerField(  # For RPI, it's RIN
        verbose_name=_('RIN'),
        unique=True,
        null=False,
        blank=False
    )

    active = models.BooleanField(  # Is this user still active in the company/system?
        verbose_name=_('Active'),
        default=True
    )

    restricted = models.BooleanField(  # Is this user able to loan items?
        verbose_name=_('Restricted'),
        default=False
    )


class LoanSession(models.Model):
    """ Represents an item being loaned to a user for a period of time."""
    @staticmethod
    def get_api_url():
        """Return API url."""
        return '/plugin/loan/api/loansession/'

    @staticmethod
    def get_end_of_day():
        """Return the very end of yesterday. This allows for a loan to not be considered overdue on the day it is due."""
        return datetime.date.today() + datetime.timedelta(milliseconds=-1)

    class Meta:
        app_label = "loanmanagement"

    # Sessions that have not been returned and are past their due date.
    OVERDUE_FILTER = Q(
        returned=False,
        due_date__lt=get_end_of_day()
    )

    # Sessions that have not been returned and are not past their due date.
    CURRENT_FILTER = Q(
        returned=False,
        due_date__gte=get_end_of_day(),
        loan_date__lte=get_end_of_day()
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
