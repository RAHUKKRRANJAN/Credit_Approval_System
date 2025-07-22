from django.core.management.base import BaseCommand
import pandas as pd
from credit_app.models import Customer, Loan
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files'

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting data ingestion...')
            )
            
            # Get absolute paths
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            customer_file = os.path.join(base_dir, 'customer_data.xlsx')
            loan_file = os.path.join(base_dir, 'loan_data.xlsx')
            
            # Print file paths
            self.stdout.write(f'Customer data file: {customer_file}')
            self.stdout.write(f'Loan data file: {loan_file}')
            
            # Ingest customer data
            self.stdout.write('Ingesting customer data...')
            df_customers = pd.read_excel(customer_file)
            
            # Print DataFrame info
            self.stdout.write('Customer data columns:')
            self.stdout.write(str(df_customers.columns.tolist()))
            self.stdout.write('First row of customer data:')
            self.stdout.write(str(df_customers.iloc[0].to_dict()))
            
            customers_created = 0
            customers_updated = 0
            
            for _, row in df_customers.iterrows():
                customer_data = {
                    'first_name': str(row['First Name']),
                    'last_name': str(row['Last Name']),
                    'age': int(row['Age']) if pd.notna(row['Age']) else 25,  # Default age if not provided
                    'monthly_salary': int(float(row['Monthly Salary'])),
                    'phone_number': str(row['Phone Number']),
                    'approved_limit': int(float(row['Approved Limit'])),
                    'current_debt': 0.0  # Initialize with 0 as it's not in the Excel
                }
                
                # Validate age
                if customer_data['age'] < 18:
                    customer_data['age'] = 18  # Minimum age requirement
                elif customer_data['age'] > 100:
                    customer_data['age'] = 100  # Maximum age cap
                
                # Check if customer exists
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
            
            self.stdout.write(
                self.style.SUCCESS(f'Customer data ingestion completed. Created: {customers_created}, Updated: {customers_updated}')
            )
            
            # Ingest loan data
            self.stdout.write('Ingesting loan data...')
            df_loans = pd.read_excel(loan_file)
            
            # Print DataFrame info
            self.stdout.write('Loan data columns:')
            self.stdout.write(str(df_loans.columns.tolist()))
            self.stdout.write('First row of loan data:')
            self.stdout.write(str(df_loans.iloc[0].to_dict()))
            
            loans_created = 0
            loans_updated = 0
            
            for _, row in df_loans.iterrows():
                try:
                    # Get customer
                    customer = Customer.objects.get(customer_id=int(row['Customer ID']))
                    
                    # Parse dates - using the correct column names from Excel
                    start_date = pd.to_datetime(row['Date of Approval']).date()
                    end_date = pd.to_datetime(row['End Date']).date()
                    
                    loan_data = {
                        'customer': customer,
                        'loan_amount': float(row['Loan Amount']),
                        'tenure': int(row['Tenure']),
                        'interest_rate': float(row['Interest Rate']),
                        'monthly_repayment': float(row['Monthly payment']),
                        'emis_paid_on_time': int(row['EMIs paid on Time']),
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    
                    # Check if loan exists
                    loan, created = Loan.objects.get_or_create(
                        loan_id=int(row['Loan ID']),
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
                    self.stdout.write(
                        self.style.WARNING(f'Customer with ID {row["Customer ID"]} not found for loan {row["Loan ID"]}')
                    )
                    continue
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing loan: {str(e)}')
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(f'Loan data ingestion completed. Created: {loans_created}, Updated: {loans_updated}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during data ingestion: {str(e)}')
            )
            logger.error(f'Error during data ingestion: {str(e)}') 