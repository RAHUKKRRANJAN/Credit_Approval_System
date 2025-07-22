import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

def print_test(title, response):
    print(f"\n{title}")
    print(f"Status Code {response.status_code}")
    print("Response")
    print(json.dumps(response.json(), indent=2))

def test_register():
    print("\nTesting Customer Registration")
    
    data = {
        "first_name": "Test",
        "last_name": "Customer",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543299"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_test("Valid Registration", response)
    
    if response.status_code == 201:
        return response.json().get('customer_id')
    return None

def test_check_eligibility(customer_id):
    print("\nTesting Loan Eligibility")
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_test("Small Loan Eligibility", response)
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 1000000,
        "interest_rate": 20,
        "tenure": 24
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_test("Large Loan Eligibility", response)

def test_create_loan(customer_id):
    print("\nTesting Loan Creation")
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/create-loan/", json=data)
    print_test("Create Loan", response)
    
    if response.status_code == 200:
        return response.json().get('loan_id')
    return None

def test_view_loan(loan_id):
    print("\nTesting View Loan")
    
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print_test("View Loan Details", response)

def test_view_loans(customer_id):
    print("\nTesting View Customer Loans")
    
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print_test("View All Loans", response)

def main():
    print("Starting Credit Approval System Tests")
    
    customer_id = test_register()
    if not customer_id:
        print("Customer registration failed Stopping tests")
        return
    
    test_check_eligibility(customer_id)
    
    loan_id = test_create_loan(customer_id)
    if not loan_id:
        print("Loan creation failed Stopping tests")
        return
    
    test_view_loan(loan_id)
    test_view_loans(customer_id)
    
    print("\nAll tests completed")

if __name__ == "__main__":
    main() 