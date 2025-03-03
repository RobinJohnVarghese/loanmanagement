from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Loan
from .serializers import LoanSerializer, CreateLoanSerializer,ForecloseLoanSerializer
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404



class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get loans for the authenticated user
        return Loan.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active_loans(self, request):
        loans = Loan.objects.filter(user=request.user, is_foreclosed=False)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def past_loans(self, request):
        loans = Loan.objects.filter(user=request.user, is_foreclosed=True)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def foreclose(self, request, pk=None):
        loan = self.get_object()
        loan.is_foreclosed = True
        loan.foreclosed_date = request.data.get('foreclosed_date')
        loan.save()
        serializer = LoanSerializer(loan)
        return Response(serializer.data)

class AdminLoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Admin can see all loans
        return Loan.objects.all()
    

class ForecloseLoanView(APIView):
    def post(self, request, loan_id):
        # Get loan instance
        loan = get_object_or_404(Loan, loan_id=loan_id)

        if loan.is_foreclosed:
            return Response({"status": "error", "message": "Loan already foreclosed."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate foreclosure discount (example: 5% of total interest)
        discount = round(loan.total_interest * 0.05, 2)  
        final_settlement_amount = round(loan.total_amount - discount, 2)

        # Update loan status
        loan.is_foreclosed = True
        loan.foreclosure_amount = final_settlement_amount
        loan.save()

        # Response
        return Response({
            "status": "success",
            "message": "Loan foreclosed successfully.",
            "data": {
                "loan_id": loan.loan_id,
                "amount_paid": float(loan.total_amount),
                "foreclosure_discount": float(discount),
                "final_settlement_amount": float(final_settlement_amount),
                "status": "CLOSED"
            }
        }, status=status.HTTP_200_OK)
    
class ForecloseLoanViewSet(viewsets.ViewSet):
    """Handles loan foreclosure requests."""

    @action(detail=True, methods=['post'], url_path='foreclose')
    def foreclose(self, request, pk=None):
        """Foreclose a loan based on its loan_id."""
        p=request.data.get("loan_id",pk)
        if p:
            loan = Loan.objects.get(loan_id=p)
        # print("222222",loan.loan_id)
        try:
            loan = Loan.objects.get(loan_id=loan.loan_id)
            if loan.is_foreclosed:
                return Response({"status": "error", "message": "Loan already foreclosed."}, status=status.HTTP_400_BAD_REQUEST)
            
            foreclosure_discount = 500.00  # Example discount
            final_settlement_amount = float(loan.amount) + float(loan.interest_rate) - foreclosure_discount  

            loan.is_foreclosed = True
            loan.status = "CLOSED"
            loan.save()
            
            return Response({
                "status": "success",
                "message": "Loan foreclosed successfully.",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount_paid": float(loan.amount) + float(loan.interest_rate),
                    "foreclosure_discount": foreclosure_discount,
                    "final_settlement_amount": final_settlement_amount,
                    "status": "CLOSED"
                }
            }, status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response({"status": "error", "message": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)
