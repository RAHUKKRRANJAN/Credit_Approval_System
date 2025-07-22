from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Customer, Loan
from .utils import calculate_credit_score, calculate_emi, check_loan_eligibility
from datetime import date, timedelta
from decimal import Decimal

class CustomerModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="9876543210",
            approved_limit=1800000
        )

    def test_phone_number_validation(self):
        """Test phone number validation"""
        with self.assertRaises(Exception):
            Customer.objects.create(
                first_name="Test",
                last_name="User",
                age=30,
                monthly_salary=50000,
                phone_number="123",  # Invalid phone number
                approved_limit=1800000
            )

    def test_age_validation(self):
        """Test age validation"""
        with self.assertRaises(Exception):
            Customer.objects.create(
                first_name="Test",
                last_name="User",
                age=15,  # Below minimum age
                monthly_salary=50000,
                phone_number="9876543211",
                approved_limit=1800000
            )

class LoanModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="9876543210",
            approved_limit=1800000
        )

    def test_loan_validation(self):
        """Test loan amount and date validation"""
        with self.assertRaises(Exception):
            Loan.objects.create(
                customer=self.customer,
                loan_amount=-1000,  # Negative amount
                tenure=12,
                interest_rate=10,
                monthly_repayment=1000,
                start_date=date.today(),
                end_date=date.today()  # Same as start date
            )

class CreditScoreTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="9876543210",
            approved_limit=1800000
        )

    def test_new_customer_credit_score(self):
        """Test credit score for new customer"""
        score = calculate_credit_score(self.customer.customer_id)
        self.assertEqual(score, 10)  # Base score for new customers

    def test_good_credit_score(self):
        """Test credit score for customer with good payment history"""
        Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8800,
            emis_paid_on_time=12,
            start_date=date.today() - timedelta(days=365),
            end_date=date.today()
        )
        score = calculate_credit_score(self.customer.customer_id)
        self.assertGreater(score, 50)

class APITests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=30,
            monthly_salary=50000,
            phone_number="9876543210",
            approved_limit=1800000
        )

    def test_register_api(self):
        """Test customer registration API"""
        url = reverse('register')
        data = {
            "first_name": "New",
            "last_name": "Customer",
            "age": 35,
            "monthly_income": 75000,
            "phone_number": "9876543211"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approved_limit'], 2700000)  # 36 * monthly_income

    def test_check_eligibility_api(self):
        """Test loan eligibility check API"""
        url = reverse('check-eligibility')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)

    def test_view_loans_api(self):
        """Test view loans API"""
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8800,
            emis_paid_on_time=6,
            start_date=date.today() - timedelta(days=180),
            end_date=date.today() + timedelta(days=180)
        )
        url = reverse('view-loans', args=[self.customer.customer_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_view_loan_api(self):
        """Test view specific loan API"""
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=100000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=8800,
            emis_paid_on_time=6,
            start_date=date.today() - timedelta(days=180),
            end_date=date.today() + timedelta(days=180)
        )
        url = reverse('view-loan', args=[loan.loan_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], loan.loan_id) 