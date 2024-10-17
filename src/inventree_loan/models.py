"""Models for LoanPlugin."""

import datetime

from django.core.validators import MinValueValidator, validate_email
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from django.conf import settings

class LoanSession(models.Model):
    """ Represents an item being loaned to a user for a period of time."""
    @staticmethod
    def get_api_url():
        """Return API url."""
        return '/plugin/loan/api/loansession/'
#        return reverse('api-loan-session-list')  #TODO: Figure out why this doesn't work

    class Meta:
        app_label = "inventree_loan"

    @staticmethod
    def get_end_of_day():
        """Return the very end of yesterday. This allows for a loan to not be considered overdue on the day it is due."""
        return datetime.date.today() + datetime.timedelta(milliseconds=-1)


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

    RETURNED_FILTER = Q(
        returned=True
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    location = models.CharField(
        max_length=250,
        verbose_name=_('Location'),
        null=True,
        blank=True
    )

    notes = models.TextField(
        verbose_name=_('Notes'),
        null=True,
        blank=True
    )

    @transaction.atomic
    def return_item(self, **kwargs):
        """
        Return the item.
        Args:
            kwargs:
                returned_date: The date the item was returned
        """
        self.returned = True
        self.returned_date = kwargs.get('returned_date', datetime.date.today())

        self.save()

        return True

    # Testing, trying to add a fake field. Didn't work (didn't run migrations though)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.user_badge = models.CharField(
            verbose_name = _('User Badge'),
        )           

