from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView

from .models import LoanUser


class LoanItemDetail(ListView):
    """Detailed view of a single StockItem object."""

    context_object_name = 'loanitems'
    template_name = 'loansessionform_temp.html'
    model = LoanUser
