#!/usr/bin/env python3
"""
Test script for Credit Approval System API endpoints
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_register():
    url = f'{BASE_URL}/register/'
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 50000,  # Changed from monthly_salary to monthly_income
        "phone_number": "9876543210"
    }
    response = requests.post(url, json=data)
    print("Register Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))
    return response.json()

def test_check_eligibility(customer_id):
    url = f'{BASE_URL}/check-eligibility/'
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 10,
        "tenure": 12
    }
    response = requests.post(url, json=data)
    print("\nEligibility Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

def test_view_loans(customer_id):
    url = f'{BASE_URL}/view-loans/{customer_id}'
    response = requests.get(url)
    print("\nView Loans Response:", response.status_code)
    print(json.dumps(response.json(), indent=2))

if __name__ == '__main__':
    # Register a new customer
    customer = test_register()
    
    if 'customer_id' in customer:
        # Check loan eligibility
        test_check_eligibility(customer['customer_id'])
        
        # View customer's loans
        test_view_loans(customer['customer_id']) 