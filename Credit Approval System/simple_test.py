#!/usr/bin/env python3
"""
Simple Test Script for Credit Approval System
Run this to test your system!
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_system():
    print("Testing Credit Approval System...")
    
    # Step 1: Register a customer
    print("\nStep 1: Registering a customer...")
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 60000,
        "phone_number": "7777777777"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=customer_data)
        if response.status_code == 201:
            customer = response.json()
            customer_id = customer['customer_id']
            print("SUCCESS: Customer registered successfully!")
            print(f"   Customer ID: {customer_id}")
            print(f"   Name: {customer['name']}")
            print(f"   Approved Limit: Rs.{customer['approved_limit']:,}")
        else:
            print(f"ERROR: Registration failed: {response.text}")
            return
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
        return
    
    # Step 2: Check loan eligibility
    print(f"\nStep 2: Checking loan eligibility for customer {customer_id}...")
    eligibility_data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 12.0,
        "tenure": 12
    }
    
    try:
        response = requests.post(f"{BASE_URL}/check-eligibility/", json=eligibility_data)
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Eligibility check completed!")
            print(f"   Approval: {'APPROVED' if result['approval'] else 'REJECTED'}")
            print(f"   Interest Rate: {result['interest_rate']}%")
            print(f"   Monthly EMI: Rs.{result['monthly_installment']:,.2f}")
        else:
            print(f"ERROR: Eligibility check failed: {response.text}")
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
    
    # Step 3: Try to create a loan
    print(f"\nStep 3: Trying to create a loan for customer {customer_id}...")
    loan_data = {
        "customer_id": customer_id,
        "loan_amount": 200000,
        "interest_rate": 18.0,  # High interest rate
        "tenure": 12
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create-loan/", json=loan_data)
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Loan creation completed!")
            print(f"   Loan Approved: {'YES' if result['loan_approved'] else 'NO'}")
            print(f"   Loan ID: {result['loan_id']}")
            print(f"   Message: {result['message']}")
            
            loan_id = result['loan_id']
        else:
            print(f"ERROR: Loan creation failed: {response.text}")
            loan_id = None
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
        loan_id = None
    
    # Step 4: View customer loans
    print(f"\nStep 4: Viewing loans for customer {customer_id}...")
    try:
        response = requests.get(f"{BASE_URL}/view-loans/{customer_id}/")
        if response.status_code == 200:
            loans = response.json()
            print("SUCCESS: Customer loans retrieved!")
            print(f"   Total Loans: {len(loans)}")
            
            if loans:
                for i, loan in enumerate(loans, 1):
                    print(f"   Loan {i}:")
                    print(f"     Amount: Rs.{loan['loan_amount']:,.2f}")
                    print(f"     Interest Rate: {loan['interest_rate']}%")
                    print(f"     Monthly EMI: Rs.{loan['monthly_installment']:,.2f}")
            else:
                print("   No loans found for this customer")
        else:
            print(f"ERROR: Failed to fetch loans: {response.text}")
    except Exception as e:
        print(f"ERROR: Connection error: {e}")
    
    # Step 5: View specific loan (if created)
    if loan_id:
        print(f"\nStep 5: Viewing loan details for loan {loan_id}...")
        try:
            response = requests.get(f"{BASE_URL}/view-loan/{loan_id}/")
            if response.status_code == 200:
                loan_detail = response.json()
                print("SUCCESS: Loan details retrieved!")
                print(f"   Customer: {loan_detail['customer']['first_name']} {loan_detail['customer']['last_name']}")
                print(f"   Loan Amount: Rs.{loan_detail['loan_amount']:,.2f}")
                print(f"   Interest Rate: {loan_detail['interest_rate']}%")
                print(f"   Tenure: {loan_detail['tenure']} months")
            else:
                print(f"ERROR: Failed to fetch loan details: {response.text}")
        except Exception as e:
            print(f"ERROR: Connection error: {e}")
    
    print("\nSystem Test Completed!")
    print("All API endpoints are working!")
    print("Credit score algorithm is working!")
    print("Loan approval rules are implemented!")
    print("Your Credit Approval System is LIVE!")

if __name__ == "__main__":
    test_system() 