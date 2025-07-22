import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

def print_result(title, response):
    print(f"\n{title}")
    print(f"Status Code {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Response Text {response.text}")

def test_invalid_registration():
    print("\nTesting Invalid Registration")
    
    # Test Case 1 Invalid Age
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 15,
        "monthly_income": 50000,
        "phone_number": "9876543201"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_result("Invalid Age Registration", response)
    
    # Test Case 2 Invalid Phone
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "123"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_result("Invalid Phone Registration", response)

def test_valid_registration():
    print("\nTesting Valid Registration")
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543202"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_result("Valid Registration", response)
    try:
        return response.json().get('customer_id') if response.status_code == 201 else None
    except:
        return None

def test_loan_eligibility_scenarios(customer_id):
    print("\nTesting Loan Eligibility Scenarios")
    
    # Test Case 1 Small Loan
    data = {
        "customer_id": customer_id,
        "loan_amount": 50000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_result("Small Loan Eligibility", response)
    
    # Test Case 2 Medium Loan
    data = {
        "customer_id": customer_id,
        "loan_amount": 500000,
        "interest_rate": 12,
        "tenure": 24
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_result("Medium Loan Eligibility", response)
    
    # Test Case 3 Large Loan
    data = {
        "customer_id": customer_id,
        "loan_amount": 2000000,
        "interest_rate": 8,
        "tenure": 36
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_result("Large Loan Eligibility", response)

def test_loan_creation(customer_id):
    print("\nTesting Loan Creation")
    
    # Try to create loan with high interest rate
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/create-loan/", json=data)
    print_result("Create Loan High Interest", response)
    try:
        return response.json().get('loan_id') if response.status_code == 200 else None
    except:
        return None

def test_view_loan_details(loan_id):
    print("\nTesting View Loan Details")
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print_result("View Loan Details", response)

def test_view_customer_loans(customer_id):
    print("\nTesting View Customer Loans")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print_result("View Customer Loans", response)

def test_edge_cases():
    print("\nTesting Edge Cases")
    
    # Invalid customer ID
    response = requests.get(f"{BASE_URL}/view-loans/99999")
    print_result("Invalid Customer ID", response)
    
    # Invalid loan ID
    response = requests.get(f"{BASE_URL}/view-loan/99999")
    print_result("Invalid Loan ID", response)
    
    # Invalid eligibility check
    data = {
        "customer_id": 99999,
        "loan_amount": -1000,
        "interest_rate": -5,
        "tenure": 0
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_result("Invalid Eligibility Check", response)

def main():
    print("Starting Comprehensive System Tests")
    
    # Test invalid registrations
    test_invalid_registration()
    
    # Test valid registration
    customer_id = test_valid_registration()
    if not customer_id:
        print("Valid registration failed Stopping tests")
        return
    
    # Test loan eligibility scenarios
    test_loan_eligibility_scenarios(customer_id)
    
    # Test loan creation
    loan_id = test_loan_creation(customer_id)
    if loan_id:
        test_view_loan_details(loan_id)
    
    # Test viewing customer loans
    test_view_customer_loans(customer_id)
    
    # Test edge cases
    test_edge_cases()
    
    print("\nAll tests completed")

if __name__ == "__main__":
    main() 