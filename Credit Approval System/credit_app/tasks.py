import pandas as pd
from celery import shared_task
from django.utils import timezone
from datetime import datetime
from .models import Customer, Loan
import logging

logger = logging.getLogger(__name__)

@shared_task
def ingest_customer_data():
    """Ingest customer data from customer_data.xlsx"""
    try:
        # Read the Excel file
        df = pd.read_excel('customer_data.xlsx')
        
        customers_created = 0
        customers_updated = 0
        
        for _, row in df.iterrows():
            customer_data = {
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'monthly_salary': int(row['monthly_salary']),
                'phone_number': str(row['phone_number']),
                'approved_limit': int(row['approved_limit']),
                'current_debt': float(row['current_debt']) if pd.notna(row['current_debt']) else 0.0
            }
            
            # Check if customer already exists
            customer, created = Customer.objects.get_or_create(
                phone_number=customer_data['phone_number'],
                defaults=customer_data
            )
            
            if created:
                customers_created += 1
            else:
                # Update existing customer
                for key, value in customer_data.items():
                    setattr(customer, key, value)
                customer.save()
                customers_updated += 1
        
        logger.info(f"Customer data ingestion completed. Created: {customers_created}, Updated: {customers_updated}")
        return f"Customer data ingestion completed. Created: {customers_created}, Updated: {customers_updated}"
        
    except Exception as e:
        logger.error(f"Error ingesting customer data: {str(e)}")
        raise

@shared_task
def ingest_loan_data():
    """Ingest loan data from loan_data.xlsx"""
    try:
        # Read the Excel file
        df = pd.read_excel('loan_data.xlsx')
        
        loans_created = 0
        loans_updated = 0
        
        for _, row in df.iterrows():
            try:
                # Get customer
                customer = Customer.objects.get(customer_id=int(row['customer_id']))
                
                # Parse dates
                start_date = pd.to_datetime(row['start_date']).date()
                end_date = pd.to_datetime(row['end_date']).date()
                
                loan_data = {
                    'customer': customer,
                    'loan_amount': float(row['loan_amount']),
                    'tenure': int(row['tenure']),
                    'interest_rate': float(row['interest_rate']),
                    'monthly_repayment': float(row['monthly_repayment']),
                    'emis_paid_on_time': int(row['EMIs_paid_on_time']),
                    'start_date': start_date,
                    'end_date': end_date
                }
                
                # Check if loan already exists
                loan, created = Loan.objects.get_or_create(
                    loan_id=int(row['loan_id']),
                    defaults=loan_data
                )
                
                if created:
                    loans_created += 1
                else:
                    # Update existing loan
                    for key, value in loan_data.items():
                        setattr(loan, key, value)
                    loan.save()
                    loans_updated += 1
                    
            except Customer.DoesNotExist:
                logger.warning(f"Customer with ID {row['customer_id']} not found for loan {row['loan_id']}")
                continue
        
        logger.info(f"Loan data ingestion completed. Created: {loans_created}, Updated: {loans_updated}")
        return f"Loan data ingestion completed. Created: {loans_created}, Updated: {loans_updated}"
        
    except Exception as e:
        logger.error(f"Error ingesting loan data: {str(e)}")
        raise

@shared_task
def ingest_all_data():
    """Ingest both customer and loan data"""
    try:
        # First ingest customers
        customer_result = ingest_customer_data.delay()
        customer_result.get()  # Wait for completion
        
        # Then ingest loans
        loan_result = ingest_loan_data.delay()
        loan_result.get()  # Wait for completion
        
        logger.info("All data ingestion completed successfully")
        return "All data ingestion completed successfully"
        
    except Exception as e:
        logger.error(f"Error in data ingestion: {str(e)}")
        raise 