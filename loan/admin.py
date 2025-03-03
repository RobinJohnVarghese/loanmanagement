from django.contrib import admin
from .models import Loan
# Register your models here.


class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'user', 'amount', 'interest_rate','tenure_months','start_date','is_foreclosed','foreclosed_date')
    list_display_links = ('loan_id', 'user')

admin.site.register(Loan, LoanAdmin)