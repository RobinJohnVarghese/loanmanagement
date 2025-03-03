from django.db import models
from django.conf import settings
from decimal import Decimal

class Loan(models.Model):
    loan_id = models.CharField(max_length=20, unique=True)  # Unique Loan ID
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.IntegerField()
    start_date = models.DateField(auto_now_add=True)
    is_foreclosed = models.BooleanField(default=False)
    foreclosed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[("ACTIVE", "Active"), ("CLOSED", "Closed")], default="ACTIVE")

    def save(self, *args, **kwargs):
        if not self.loan_id:  # Only generate loan_id if it is not already set
            last_loan = Loan.objects.order_by('-id').first()
            new_id = last_loan.id + 1 if last_loan else 1
            self.loan_id = f"LOAN{new_id:03d}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Loan {self.id} - {self.user.email}"
    
    def get_monthly_installment(self):
        # Basic formula to calculate monthly installment without considering principal reduction
        principal = float(self.amount)
        interest = float(self.amount) * (float(self.interest_rate) / 100)
        total_amount = principal + interest
        return round(total_amount / self.tenure_months, 2)
    
    def get_total_interest(self):
        # Total interest on the loan
        return round(float(self.amount) * (float(self.interest_rate) / 100), 2)
    
    def get_foreclosure_discount(self, remaining_months):
        """Calculate foreclosure discount (5% of remaining interest)"""
        remaining_interest = (self.amount * (self.interest_rate / Decimal(100)) * Decimal(remaining_months) / Decimal(12))
        return round(Decimal(0.05) * remaining_interest, 2)

    def get_foreclosure_amount(self):
        """Calculate foreclosure amount"""
        months_paid = (self.start_date - self.start_date).days // 30  # Placeholder for actual calculation
        remaining_months = self.tenure_months - months_paid

        if remaining_months <= 0:
            return self.amount + self.get_total_interest(), 0.0  # No discount if tenure is completed

        foreclosure_discount = self.get_foreclosure_discount(remaining_months)
        final_amount = (self.amount + (self.get_total_interest() * remaining_months / self.tenure_months)) - foreclosure_discount

        return round(final_amount, 2), foreclosure_discount
