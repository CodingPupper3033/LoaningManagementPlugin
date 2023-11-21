from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView

from .models import LoanUser, LoanSession


class LoanItemDetail(ListView):
    """Detailed view of a single StockItem object."""

    context_object_name = 'loanitems'
    template_name = 'loansessionform_temp.html'
    model = LoanUser


class LoanTrackingDetail(ListView):
    """Detailed view of loan sessions"""

    context_object_name = 'loanitems'
    template_name = 'tracking.html'
    model = LoanSession

    def get_context_data(self, **kwargs):
        """Extend template context."""
        context = super().get_context_data(**kwargs)

        # Get the counts of different categories of loan sessions
        context['overdue_count'] = LoanSession.objects.filter(LoanSession.OVERDUE_FILTER).count()
        context['current_count'] = LoanSession.objects.filter(LoanSession.CURRENT_FILTER).count()

        return context
