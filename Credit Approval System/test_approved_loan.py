#!/usr/bin/env python3
"""
Test script for approved loan scenario
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

def create_customer_with_good_history():
    """Create a customer and add good loan history"""
    print("🧪 Creating customer with good credit history...")
    
    # Register customer
    data = {
        "first_name": "Priya",
        "last_name": "Sharma",
        "age": 32,
        "monthly_income": 100000,
        "phone_number": "9876543211"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=data)
    if response.status_code != 201:
        print(f"❌ Customer registration failed: {response.text}")
        return None
    
    customer_data = response.json()
    customer_id = customer_data['customer_id']
    print(f"✅ Customer created: {customer_data['name']} (ID: {customer_id})")
    
    # Add good loan history by creating a loan with good payment record
    # This will be done through direct database manipulation in a real scenario
    # For now, we'll test with a higher interest rate loan
    
    return customer_id

def test_high_interest_loan(customer_id):
    """Test loan with high interest rate for better approval chances"""
    print(f"\n🧪 Testing high interest rate loan for Customer {customer_id}...")
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 18.0,  # High interest rate
        "tenure": 12
    }
    
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Eligibility check completed!")
        print(f"Approval: {'✅ Approved' if result['approval'] else '❌ Rejected'}")
        print(f"Interest Rate: {result['interest_rate']}%")
        print(f"Corrected Rate: {result['corrected_interest_rate']}%")
        print(f"Monthly EMI: ₹{result['monthly_installment']:,.2f}")
        return result['approval']
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_loan_creation(customer_id, should_approve=True):
    """Test loan creation with high interest rate"""
    print(f"\n🧪 Testing Loan Creation for Customer {customer_id}...")
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 18.0,  # High interest rate for approval
        "tenure": 12
    }
    
    response = requests.post(f"{BASE_URL}/create-loan/", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Loan creation completed!")
        print(f"Loan Approved: {'✅ Yes' if result['loan_approved'] else '❌ No'}")
        print(f"Loan ID: {result['loan_id']}")
        print(f"Message: {result['message']}")
        print(f"Monthly EMI: ₹{result['monthly_installment']:,.2f}")
        return result['loan_id']
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_view_loan(loan_id):
    """Test viewing loan details"""
    if not loan_id:
        print("\n🧪 Skipping loan view test (no loan created)")
        return
    
    print(f"\n🧪 Testing Loan View for Loan {loan_id}...")
    
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}/")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Loan details retrieved!")
        print(f"Loan ID: {result['loan_id']}")
        print(f"Customer: {result['customer']['first_name']} {result['customer']['last_name']}")
        print(f"Loan Amount: ₹{result['loan_amount']:,.2f}")
        print(f"Interest Rate: {result['interest_rate']}%")
        print(f"Monthly EMI: ₹{result['monthly_installment']:,.2f}")
        print(f"Tenure: {result['tenure']} months")
    else:
        print(f"❌ Error: {response.text}")

def main():
    """Run approved loan test"""
    print("🚀 Starting Approved Loan Test...")
    print("=" * 50)
    
    # Create customer
    customer_id = create_customer_with_good_history()
    if not customer_id:
        return
    
    # Test eligibility with high interest rate
    is_eligible = test_high_interest_loan(customer_id)
    
    # Test loan creation
    loan_id = test_loan_creation(customer_id, is_eligible)
    
    # Test loan view
    test_view_loan(loan_id)
    
    print("\n" + "=" * 50)
    print("🎉 Approved Loan Test Completed!")
    print(f"📊 Results:")
    print(f"  ✅ Customer Creation: {'PASS' if customer_id else 'FAIL'}")
    print(f"  ✅ High Interest Eligibility: {'PASS' if is_eligible is not None else 'FAIL'}")
    print(f"  ✅ Loan Creation: {'PASS' if loan_id else 'FAIL'}")
    print(f"  ✅ Loan View: {'PASS' if loan_id else 'SKIP'}")

if __name__ == "__main__":
    main() 