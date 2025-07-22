from rest_framework import serializers
from .models import Customer, Loan
from datetime import date

# Register endpoint serializers
class RegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    age = serializers.IntegerField(min_value=18, max_value=100)
    monthly_income = serializers.IntegerField(min_value=0)
    phone_number = serializers.CharField(max_length=20)

class RegisterResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.IntegerField(source='monthly_salary')

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

# Check eligibility endpoint serializers
class CheckEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()

# Create loan endpoint serializers
class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField(min_value=0)
    interest_rate = serializers.FloatField(min_value=0)
    tenure = serializers.IntegerField(min_value=1)

class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField()

# View loan endpoint serializers
class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']

class ViewLoanResponseSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer()
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=10, decimal_places=2)

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

# View customer loans endpoint serializers
class ViewCustomerLoansResponseSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    monthly_installment = serializers.DecimalField(source='monthly_repayment', max_digits=10, decimal_places=2)

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']

    def get_repayments_left(self, obj):
        """Calculate remaining EMIs based on start date and current date"""
        if obj.end_date <= date.today():
            return 0
        
        # Calculate months passed since start
        months_passed = (date.today().year - obj.start_date.year) * 12 + (date.today().month - obj.start_date.month)
        repayments_left = obj.tenure - months_passed
        
        return max(repayments_left, 0) 