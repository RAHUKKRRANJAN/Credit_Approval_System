from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Customer, Loan
from .serializers import (
    RegisterRequestSerializer, RegisterResponseSerializer,
    CheckEligibilityRequestSerializer, CheckEligibilityResponseSerializer,
    CreateLoanRequestSerializer, CreateLoanResponseSerializer,
    ViewLoanResponseSerializer, ViewCustomerLoansResponseSerializer
)
from .utils import check_loan_eligibility, calculate_emi
import math
from datetime import date

class RegisterView(APIView):
    """Register a new customer"""
    
    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Calculate approved limit: 36 * monthly_salary (rounded to nearest lakh)
        monthly_income = data['monthly_income']
        approved_limit = round(36 * monthly_income / 100000) * 100000
        
        # Check if phone number already exists
        if Customer.objects.filter(phone_number=data['phone_number']).exists():
            return Response(
                {"error": "Phone number already registered"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create customer
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_salary=monthly_income,
            phone_number=data['phone_number'],
            approved_limit=approved_limit
        )
        
        response_serializer = RegisterResponseSerializer(customer)
        return Response(
            response_serializer.data, 
            status=status.HTTP_201_CREATED
        )

class CheckEligibilityView(APIView):
    """Check loan eligibility for a customer"""
    
    def post(self, request):
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check eligibility
        eligibility_result = check_loan_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        response_data = {
            "customer_id": data['customer_id'],
            "approval": eligibility_result['approval'],
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": eligibility_result['corrected_interest_rate'],
            "tenure": data['tenure'],
            "monthly_installment": eligibility_result['monthly_installment']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    """Create a new loan for a customer"""
    
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = serializer.validated_data
        
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check eligibility
        eligibility_result = check_loan_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        loan_id = None
        message = "Loan approved successfully"
        
        if eligibility_result['approval']:
            # Create the loan
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=eligibility_result['corrected_interest_rate'],
                monthly_repayment=eligibility_result['monthly_installment'],
                emis_paid_on_time=0,  # New loan, no EMIs paid yet
                start_date=date.today(),
                end_date=date.today().replace(
                    year=date.today().year + (data['tenure'] // 12),
                    month=date.today().month + (data['tenure'] % 12)
                )
            )
            loan_id = loan.loan_id
        else:
            message = eligibility_result.get('reason', 'Loan not approved based on eligibility criteria')
        
        response_data = {
            "loan_id": loan_id,
            "customer_id": data['customer_id'],
            "loan_approved": eligibility_result['approval'],
            "message": message,
            "monthly_installment": eligibility_result['monthly_installment']
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class ViewLoanView(APIView):
    """View details of a specific loan"""
    
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {"error": "Loan not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ViewLoanResponseSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewCustomerLoansView(APIView):
    """View all loans for a specific customer"""
    
    def get(self, request, customer_id):
        # Check if customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        loans = Loan.objects.filter(customer_id=customer_id)
        serializer = ViewCustomerLoansResponseSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 