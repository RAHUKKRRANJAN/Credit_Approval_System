import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000/api'

def print_test_header(title):
    print("\n")
    print("Testing", title)
    print("Request URL", BASE_URL + title)

def print_response(response):
    print("\nResponse Status", response.status_code)
    print("Response Body")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_register_api():
    print_test_header("/register")
    
    print("\nTest 1 Register new customer with valid data")
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9876543222"
    }
    print("Request Body")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/register/", json=data)
    print_response(response)
    return response.json().get('customer_id') if response.status_code == 201 else None

def test_check_eligibility_api(customer_id):
    print_test_header("/check-eligibility")
    
    print("\nTest 1 Check eligibility for small loan")
    data = {
        "customer_id": customer_id,
        "loan_amount": 50000,
        "interest_rate": 16,
        "tenure": 12
    }
    print("Request Body")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_response(response)
    
    print("\nTest 2 Check eligibility for large loan")
    data = {
        "customer_id": customer_id,
        "loan_amount": 1000000,
        "interest_rate": 12,
        "tenure": 24
    }
    print("Request Body")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/check-eligibility/", json=data)
    print_response(response)

def test_create_loan_api(customer_id):
    print_test_header("/create-loan")
    
    print("\nTest 1 Create loan with high interest")
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    print("Request Body")
    print(json.dumps(data, indent=2))
    
    response = requests.post(f"{BASE_URL}/create-loan/", json=data)
    print_response(response)
    return response.json().get('loan_id') if response.status_code == 200 and response.json().get('loan_approved') else None

def test_view_loan_api(loan_id):
    print_test_header(f"/view-loan/{loan_id}")
    
    print("\nTest 1 View specific loan details")
    response = requests.get(f"{BASE_URL}/view-loan/{loan_id}")
    print_response(response)

def test_view_loans_api(customer_id):
    print_test_header(f"/view-loans/{customer_id}")
    
    print("\nTest 1 View all loans for customer")
    response = requests.get(f"{BASE_URL}/view-loans/{customer_id}")
    print_response(response)

def test_existing_data():
    print_test_header("Existing Data Check")
    
    print("\nTest 1 View loans for customer ID 1")
    response = requests.get(f"{BASE_URL}/view-loans/1")
    print_response(response)
    
    print("\nTest 2 View loan ID 5930")
    response = requests.get(f"{BASE_URL}/view-loan/5930")
    print_response(response)

def main():
    print("Starting Detailed API Tests")
    
    # Test register API
    customer_id = test_register_api()
    if not customer_id:
        print("\nCustomer registration failed Cannot continue tests")
        return
    
    print(f"\nNew customer created with ID {customer_id}")
    
    # Test check eligibility API
    test_check_eligibility_api(customer_id)
    
    # Test create loan API
    loan_id = test_create_loan_api(customer_id)
    if loan_id:
        print(f"\nNew loan created with ID {loan_id}")
        test_view_loan_api(loan_id)
    
    # Test view loans API
    test_view_loans_api(customer_id)
    
    # Test existing data
    test_existing_data()
    
    print("\nAll API tests completed")

if __name__ == "__main__":
    main() 