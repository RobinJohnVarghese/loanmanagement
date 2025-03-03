from rest_framework import serializers
from .models import Loan
from datetime import datetime, timedelta
from decimal import Decimal

class LoanSerializer(serializers.ModelSerializer):
    loan_id = serializers.SerializerMethodField()
    monthly_installment = serializers.SerializerMethodField()
    total_interest = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    payment_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'amount', 'tenure_months', 'interest_rate', 'monthly_installment', 'total_interest', 'total_amount', 'payment_schedule','status']

    def get_loan_id(self, obj):
        """Generate a unique loan ID (e.g., LOAN001)"""
        return f"LOAN{obj.id:03d}"

    def get_monthly_installment(self, obj):
        return round(obj.get_monthly_installment(), 2)

    def get_total_interest(self, obj):
        return round(obj.get_total_interest(), 2)

    def get_total_amount(self, obj):
        """Total repayment amount (Principal + Total Interest)"""
        total_interest = Decimal(str(obj.get_total_interest()))  # Convert float to Decimal
        return round(obj.amount + total_interest, 2)
        # return round(obj.amount + obj.get_total_interest(), 2)

    def get_payment_schedule(self, obj):
        """Generate a list of installment payments"""
        schedule = []
        start_date = obj.start_date
        installment_amount = round(obj.get_monthly_installment(), 2)

        for i in range(obj.tenure_months):
            due_date = start_date + timedelta(days=30 * (i + 1))  # Approximate monthly due date
            schedule.append({
                "installment_no": i + 1,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "amount": installment_amount
            })

        return schedule

    def to_representation(self, instance):
        """Format the response to match the required structure"""
        response = {
            "status": "success",
            "data": super().to_representation(instance)
        }
        return response

class CreateLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'tenure_months']

    def validate_amount(self, value):
        """Validate loan amount between ₹1,000 and ₹100,000"""
        if value < 1000 or value > 100000:
            raise serializers.ValidationError("Amount must be between ₹1,000 and ₹100,000")
        return value

    def validate_tenure_months(self, value):
        """Validate tenure between 3 and 24 months"""
        if not isinstance(value, int):
            raise serializers.ValidationError("Tenure must be a whole number")
        if value < 3 or value > 24:
            raise serializers.ValidationError("Tenure must be between 3 and 24 months")
        return value

    def create(self, validated_data):
        """Override create method to return formatted response"""
        loan = Loan.objects.create(**validated_data)
        return loan

class ForecloseLoanSerializer(serializers.ModelSerializer):
    loan_id = serializers.CharField()
    amount_paid = serializers.SerializerMethodField()
    foreclosure_discount = serializers.SerializerMethodField()
    final_settlement_amount = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ["loan_id", "amount_paid", "foreclosure_discount", "final_settlement_amount", "status"]

    def get_amount_paid(self, obj):
        return obj.amount + obj.get_total_interest()

    def get_foreclosure_discount(self, obj):
        _, discount = obj.get_foreclosure_amount()
        return discount

    def get_final_settlement_amount(self, obj):
        final_amount, _ = obj.get_foreclosure_amount()
        return final_amount

