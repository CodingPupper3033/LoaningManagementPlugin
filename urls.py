from django.urls import include, re_path

from .api import loan_session_api_urls, loan_user_api_urls

api_patterns = [
    re_path(r'^loansession/', include(loan_session_api_urls)),
    re_path(r'^loanuser/', include(loan_user_api_urls)),
]