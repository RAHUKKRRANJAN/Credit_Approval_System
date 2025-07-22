#!/usr/bin/env python3
"""
Comprehensive Demo Test for Credit Approval System
"""

import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

def print_response(title, response):
    print(f"\n{title}")
    print("Status", response.status_code)
    print(json.dumps(response.json(), indent=2))
    print()

def test_high_salary_customer():
    data = {
        "first_name": "Rich",
        "last_name": "Customer",
        "age": 35,
        "monthly_income": 200000,
        "phone_number": "9876543211"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_response("High Salary Customer Registration", response)
    return response.json().get('customer_id')

def test_low_salary_customer():
    data = {
        "first_name": "Budget",
        "last_name": "Customer",
        "age": 25,
        "monthly_income": 25000,
        "phone_number": "9876543212"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_response("Low Salary Customer Registration", response)
    return response.json().get('customer_id')

def test_loan_eligibility(customer_id, loan_amount, interest_rate=10, tenure=12):
    data = {
        "customer_id": customer_id,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "tenure": tenure
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_response(f"Loan Eligibility Check Amount {loan_amount}", response)
    return response.json()

def test_view_existing_customer_loans():
    response = requests.get(f"{BASE_URL}/view-loans/1")
    print_response("Existing Customer Loans", response)

def test_view_specific_loan():
    response = requests.get(f"{BASE_URL}/view-loan/5930")
    print_response("Specific Loan Details", response)

def run_all_tests():
    print("Starting comprehensive tests")
    
    rich_customer_id = test_high_salary_customer()
    if rich_customer_id:
        test_loan_eligibility(rich_customer_id, 100000)
        test_loan_eligibility(rich_customer_id, 1000000)
        test_loan_eligibility(rich_customer_id, 5000000)
    
    budget_customer_id = test_low_salary_customer()
    if budget_customer_id:
        test_loan_eligibility(budget_customer_id, 50000)
        test_loan_eligibility(budget_customer_id, 500000)
        test_loan_eligibility(budget_customer_id, 2000000)
    
    test_view_existing_customer_loans()
    test_view_specific_loan()

if __name__ == "__main__":
    run_all_tests() 