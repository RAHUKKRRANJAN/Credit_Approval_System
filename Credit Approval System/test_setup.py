#!/usr/bin/env python3
"""
Test script to verify the Credit Approval System setup
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_approval_system.settings')
django.setup()

from credit_app.models import Customer, Loan
from credit_app.utils import calculate_credit_score, calculate_emi, check_loan_eligibility

def test_basic_functionality():
    """Test basic functionality of the system"""
    print("Testing Credit Approval System...")
    
    # Test 1: Create a customer
    print("\n1. Testing customer creation...")
    try:
        customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="1234567890",
            approved_limit=1800000
        )
        print(f"✓ Customer created successfully: {customer.first_name} {customer.last_name}")
    except Exception as e:
        print(f"✗ Error creating customer: {e}")
        return False
    
    # Test 2: Calculate credit score
    print("\n2. Testing credit score calculation...")
    try:
        score = calculate_credit_score(customer.customer_id)
        print(f"✓ Credit score calculated: {score}")
    except Exception as e:
        print(f"✗ Error calculating credit score: {e}")
        return False
    
    # Test 3: Calculate EMI
    print("\n3. Testing EMI calculation...")
    try:
        emi = calculate_emi(100000, 10.0, 12)
        print(f"✓ EMI calculated: {emi}")
    except Exception as e:
        print(f"✗ Error calculating EMI: {e}")
        return False
    
    # Test 4: Check loan eligibility
    print("\n4. Testing loan eligibility...")
    try:
        eligibility = check_loan_eligibility(customer.customer_id, 100000, 10.0, 12)
        print(f"✓ Loan eligibility checked: {eligibility}")
    except Exception as e:
        print(f"✗ Error checking loan eligibility: {e}")
        return False
    
    # Test 5: Create a loan
    print("\n5. Testing loan creation...")
    try:
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10.0,
            monthly_repayment=8792,
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today().replace(year=date.today().year + 1)
        )
        print(f"✓ Loan created successfully: Loan ID {loan.loan_id}")
    except Exception as e:
        print(f"✗ Error creating loan: {e}")
        return False
    
    # Clean up
    print("\n6. Cleaning up test data...")
    try:
        loan.delete()
        customer.delete()
        print("✓ Test data cleaned up successfully")
    except Exception as e:
        print(f"✗ Error cleaning up: {e}")
    
    print("\n🎉 All tests passed! The system is working correctly.")
    return True

if __name__ == "__main__":
    from datetime import date
    success = test_basic_functionality()
    if not success:
        print("\n❌ Some tests failed. Please check the setup.")
        sys.exit(1) 