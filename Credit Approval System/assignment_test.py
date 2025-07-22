import requests
import json
import math

BASE_URL = 'http://localhost:8000/api'

def print_section(title):
    print("\n" + title)

def print_request(method, endpoint, data=None):
    print("\nRequest")
    print("Method", method)
    print("Endpoint", endpoint)
    if data:
        print("Body")
        print(json.dumps(data, indent=2))

def print_response(response):
    print("\nResponse")
    print("Status", response.status_code)
    print("Body")
    print(json.dumps(response.json(), indent=2))

def test_register_api():
    print_section("1 Testing Customer Registration")
    endpoint = "/register/"
    
    monthly_income = 50000
    expected_limit = math.floor(36 * monthly_income / 100000) * 100000  # Round to nearest lakh
    
    data = {
        "first_name": "Test",
        "last_name": "User",
        "age": 30,
        "monthly_income": monthly_income,
        "phone_number": "9876543255"
    }
    
    print_request("POST", endpoint, data)
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    print_response(response)
    
    if response.status_code == 201:
        result = response.json()
        print("\nValidation")
        print("Approved limit calculation", f"36 * {monthly_income} = {36 * monthly_income}")
        print("Expected limit", expected_limit)
        print("Actual limit", result["approved_limit"])
        print("Limit calculation correct", result["approved_limit"] == expected_limit)
        return result["customer_id"]
    return None

def test_check_eligibility_api(customer_id):
    print_section("2 Testing Loan Eligibility Check")
    endpoint = "/check-eligibility/"
    
    test_cases = [
        {
            "name": "Small loan high interest",
            "data": {
                "customer_id": customer_id,
                "loan_amount": 50000,
                "interest_rate": 16,
                "tenure": 12
            }
        },
        {
            "name": "Medium loan medium interest",
            "data": {
                "customer_id": customer_id,
                "loan_amount": 500000,
                "interest_rate": 12,
                "tenure": 24
            }
        },
        {
            "name": "Large loan low interest",
            "data": {
                "customer_id": customer_id,
                "loan_amount": 1000000,
                "interest_rate": 8,
                "tenure": 36
            }
        }
    ]
    
    for test in test_cases:
        print(f"\nTest case {test['name']}")
        print_request("POST", endpoint, test["data"])
        response = requests.post(f"{BASE_URL}{endpoint}", json=test["data"])
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print("\nValidation")
            print("Credit score rules")
            print("1 If credit_rating > 50 any interest rate allowed")
            print("2 If 30 < credit_rating <= 50 interest rate must be > 12%")
            print("3 If 10 < credit_rating <= 30 interest rate must be > 16%")
            print("4 If credit_rating <= 10 no loans approved")
            if not result["approval"]:
                print("Loan not approved as expected for new customer")

def test_create_loan_api(customer_id):
    print_section("3 Testing Loan Creation")
    endpoint = "/create-loan/"
    
    data = {
        "customer_id": customer_id,
        "loan_amount": 100000,
        "interest_rate": 16,
        "tenure": 12
    }
    
    print_request("POST", endpoint, data)
    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
    print_response(response)
    
    if response.status_code == 200:
        result = response.json()
        print("\nValidation")
        if result["loan_approved"]:
            print("Loan ID present", result["loan_id"] is not None)
            print("Monthly installment calculated", result["monthly_installment"] > 0)
        else:
            print("Loan rejected with message", result["message"])
        return result["loan_id"]
    return None

def test_view_loan_api(loan_id):
    print_section("4 Testing View Loan Details")
    endpoint = f"/view-loan/{loan_id}"
    
    print_request("GET", endpoint)
    response = requests.get(f"{BASE_URL}{endpoint}")
    print_response(response)
    
    if response.status_code == 200:
        result = response.json()
        print("\nValidation")
        print("Loan details present")
        print("1 Loan ID", result["loan_id"] == loan_id)
        print("2 Customer details included", "customer" in result)
        print("3 Loan amount present", "loan_amount" in result)
        print("4 Interest rate present", "interest_rate" in result)
        print("5 Monthly installment present", "monthly_installment" in result)
        print("6 Tenure present", "tenure" in result)

def test_view_loans_api(customer_id):
    print_section("5 Testing View Customer Loans")
    endpoint = f"/view-loans/{customer_id}"
    
    print_request("GET", endpoint)
    response = requests.get(f"{BASE_URL}{endpoint}")
    print_response(response)
    
    if response.status_code == 200:
        loans = response.json()
        print("\nValidation")
        print("Response is list", isinstance(loans, list))
        if loans:
            first_loan = loans[0]
            print("Loan details present")
            print("1 Loan ID present", "loan_id" in first_loan)
            print("2 Loan amount present", "loan_amount" in first_loan)
            print("3 Interest rate present", "interest_rate" in first_loan)
            print("4 Monthly installment present", "monthly_installment" in first_loan)
            print("5 Repayments left present", "repayments_left" in first_loan)

def test_error_handling():
    print_section("6 Testing Error Handling")
    
    test_cases = [
        {
            "name": "Invalid customer registration",
            "method": "POST",
            "endpoint": "/register/",
            "data": {
                "first_name": "Test",
                "last_name": "User",
                "age": 15,  # Invalid age
                "monthly_income": -1000,  # Invalid income
                "phone_number": "123"  # Invalid phone
            }
        },
        {
            "name": "Invalid loan eligibility check",
            "method": "POST",
            "endpoint": "/check-eligibility/",
            "data": {
                "customer_id": 99999,  # Non-existent customer
                "loan_amount": -1000,  # Invalid amount
                "interest_rate": -5,  # Invalid rate
                "tenure": 0  # Invalid tenure
            }
        },
        {
            "name": "Invalid loan creation",
            "method": "POST",
            "endpoint": "/create-loan/",
            "data": {
                "customer_id": 99999,
                "loan_amount": -1000,
                "interest_rate": -5,
                "tenure": 0
            }
        },
        {
            "name": "Invalid loan view",
            "method": "GET",
            "endpoint": "/view-loan/99999"  # Non-existent loan
        },
        {
            "name": "Invalid customer loans view",
            "method": "GET",
            "endpoint": "/view-loans/99999"  # Non-existent customer
        }
    ]
    
    for test in test_cases:
        print(f"\nTest case {test['name']}")
        print_request(test["method"], test["endpoint"], test.get("data"))
        
        if test["method"] == "POST":
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test["data"])
        else:
            response = requests.get(f"{BASE_URL}{test['endpoint']}")
            
        print_response(response)
        print("Validation")
        print("Error status code", response.status_code >= 400)
        print("Error message present", "error" in response.json() or response.status_code == 400)

def main():
    print("Starting Assignment Requirements Test")
    
    # Test 1 Register new customer
    customer_id = test_register_api()
    if not customer_id:
        print("\nCustomer registration failed Cannot continue tests")
        return
        
    # Test 2 Check loan eligibility
    test_check_eligibility_api(customer_id)
    
    # Test 3 Create loan
    loan_id = test_create_loan_api(customer_id)
    if loan_id:
        # Test 4 View loan details
        test_view_loan_api(loan_id)
    
    # Test 5 View customer loans
    test_view_loans_api(customer_id)
    
    # Test 6 Error handling
    test_error_handling()
    
    print("\nAll assignment requirements tested")

if __name__ == "__main__":
    main() 