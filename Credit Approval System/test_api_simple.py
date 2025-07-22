import requests
import json

BASE_URL = 'http://localhost:8000/api'

def print_result(title, response):
    print(f"\n{title}")
    print(f"Status Code {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_register_customer():
    print("\nRegistering new customer")
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543288"
    }
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_result("Register Response", response)
    return response.json().get('customer_id') if response.status_code == 201 else None

def test_check_eligibility(customer_id):
    print("\nChecking loan eligibility")
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_result("Eligibility Response", response)
    return response.json().get('approval') if response.status_code == 200 else False

def test_create_loan(customer_id):
    print("\nCreating new loan")
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    response = requests.post(f"{BASE_URL}/create-loan/", json=data)
    print_result("Create Loan Response", response)
    return response.json().get('loan_id') if response.status_code == 200 else None

def test_view_loan(loan_id):
    print("\nViewing loan details")
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print_result("View Loan Response", response)

def test_view_customer_loans(customer_id):
    print("\nViewing customer loans")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print_result("View Customer Loans Response", response)

def main():
    print("Testing Credit Approval System")
    
    customer_id = test_register_customer()
    if not customer_id:
        print("Customer registration failed")
        return
    
    is_eligible = test_check_eligibility(customer_id)
    if not is_eligible:
        print("Customer not eligible for loan")
    
    loan_id = test_create_loan(customer_id)
    if loan_id:
        test_view_loan(loan_id)
    
    test_view_customer_loans(customer_id)
    
    print("\nTesting completed")

if __name__ == "__main__":
    main() 