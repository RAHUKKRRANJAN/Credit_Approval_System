import logging
from datetime import datetime
from .models import Customer, Loan
from django.db.models import Sum, Count
from django.utils import timezone

logger = logging.getLogger(__name__)

def calculate_credit_score(customer_id):
    """
    Calculate credit score (0-100) based on multiple factors
    """
    try:
        customer = Customer.objects.get(pk=customer_id)
        loans = Loan.objects.filter(customer=customer)
        
        if not loans.exists():
            logger.info(f"Customer {customer_id} has no loan history. Assigning base score.")
            return 10  # Base score for new customers
        
        score = 0
        total_weight = 0
        
        # Component 1: Past Loans paid on time (25 points)
        weight = 25
        total_weight += weight
        if loans:
            on_time_ratio = sum(loan.emis_paid_on_time for loan in loans) / sum(
                ((loan.end_date.year - loan.start_date.year) * 12 + 
                 loan.end_date.month - loan.start_date.month) 
                for loan in loans
            )
            score += weight * min(1.0, on_time_ratio)
            logger.debug(f"On-time payment score: {weight * min(1.0, on_time_ratio)}")
        
        # Component 2: Number of loans taken (20 points)
        weight = 20
        total_weight += weight
        num_loans = loans.count()
        if num_loans <= 3:
            score += weight  # Good: Few loans
        elif num_loans <= 5:
            score += weight * 0.7  # Okay: Moderate number of loans
        else:
            score += weight * 0.4  # Caution: Many loans
        logger.debug(f"Number of loans score: {score}")
        
        # Component 3: Loan activity in current year (15 points)
        weight = 15
        total_weight += weight
        current_year = timezone.now().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        if current_year_loans == 0:
            score += weight  # Good: No new loans this year
        elif current_year_loans == 1:
            score += weight * 0.7  # Okay: One new loan
        else:
            score += weight * 0.3  # Caution: Multiple new loans
        logger.debug(f"Current year activity score: {score}")
        
        # Component 4: Loan approved volume vs salary (25 points)
        weight = 25
        total_weight += weight
        total_loan_amount = sum(loan.loan_amount for loan in loans)
        yearly_salary = customer.monthly_salary * 12
        loan_to_income_ratio = total_loan_amount / yearly_salary if yearly_salary > 0 else float('inf')
        
        if loan_to_income_ratio <= 1:
            score += weight  # Good: Total loans less than yearly salary
        elif loan_to_income_ratio <= 2:
            score += weight * 0.7  # Okay: Total loans up to 2x yearly salary
        else:
            score += weight * 0.3  # Caution: High loan to income ratio
        logger.debug(f"Loan volume score: {score}")
        
        # Component 5: Current loans vs approved limit (15 points)
        weight = 15
        total_weight += weight
        current_loans = loans.filter(end_date__gte=timezone.now().date())
        current_debt = sum(loan.loan_amount for loan in current_loans)
        
        if current_debt <= customer.approved_limit:
            score += weight  # Good: Within approved limit
            logger.debug(f"Current debt score: {weight}")
        else:
            score = 0  # Critical: Exceeded approved limit
            logger.warning(f"Customer {customer_id} has exceeded approved limit")
        
        # Normalize score to 100 points
        final_score = min(100, (score / total_weight) * 100)
        logger.info(f"Final credit score for customer {customer_id}: {final_score}")
        return final_score
        
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return 0
    except Exception as e:
        logger.error(f"Error calculating credit score for customer {customer_id}: {str(e)}")
        return 0

def calculate_emi(principal, annual_rate, tenure_months):
    """
    Calculate EMI using compound interest formula
    P * r * (1 + r)^n / ((1 + r)^n - 1)
    where:
    P = Principal
    r = Monthly interest rate (annual rate / 12 / 100)
    n = Total number of months
    """
    try:
        if tenure_months <= 0:
            raise ValueError("Tenure must be greater than 0")
        
        if annual_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 12 / 100
        
        # Calculate EMI
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = (principal * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
        
        logger.debug(f"EMI calculated: {emi} for principal: {principal}, rate: {annual_rate}, tenure: {tenure_months}")
        return round(emi, 2)
        
    except Exception as e:
        logger.error(f"Error calculating EMI: {str(e)}")
        raise

def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure_months):
    """
    Check loan eligibility based on credit score and other factors
    """
    try:
        customer = Customer.objects.get(pk=customer_id)
        credit_score = calculate_credit_score(customer_id)
        logger.info(f"Checking loan eligibility for customer {customer_id} with credit score {credit_score}")
        
        # Calculate monthly installment
        monthly_installment = calculate_emi(loan_amount, interest_rate, tenure_months)
        
        # Get current EMIs
        current_loans = Loan.objects.filter(
            customer=customer,
            end_date__gte=timezone.now().date()
        )
        current_emis = sum(loan.monthly_repayment for loan in current_loans)
        
        # Check if total EMIs exceed 50% of monthly salary
        total_emis = current_emis + monthly_installment
        if total_emis > (0.5 * customer.monthly_salary):
            logger.warning(f"Customer {customer_id} EMIs ({total_emis}) exceed 50% of salary ({customer.monthly_salary})")
            return {
                'approval': False,
                'corrected_interest_rate': interest_rate,
                'monthly_installment': 0
            }
        
        # Determine approval and interest rate based on credit score
        if credit_score > 50:
            approval = True
            corrected_rate = interest_rate
        elif 30 < credit_score <= 50 and interest_rate >= 12:
            approval = True
            corrected_rate = max(interest_rate, 12)
        elif 10 < credit_score <= 30 and interest_rate >= 16:
            approval = True
            corrected_rate = max(interest_rate, 16)
        else:
            approval = False
            corrected_rate = interest_rate
        
        if approval:
            monthly_installment = calculate_emi(loan_amount, corrected_rate, tenure_months)
        else:
            monthly_installment = 0
        
        logger.info(f"Loan eligibility result for customer {customer_id}: Approved={approval}, Rate={corrected_rate}")
        return {
            'approval': approval,
            'corrected_interest_rate': corrected_rate,
            'monthly_installment': monthly_installment
        }
        
    except Customer.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error checking loan eligibility: {str(e)}")
        raise 