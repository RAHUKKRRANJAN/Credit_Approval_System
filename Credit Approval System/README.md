# Credit Approval System

Backend system for credit approval and loan management built with Django 4+ and Django Rest Framework

## 🚀 Single Command Setup

```bash
# Start all services (DB, Web, Redis, Celery)
docker-compose up --build

# In a new terminal, after services are up (wait 1-2 minutes)
docker-compose exec web python manage.py ingest_data
```

That's it! The system is ready at http://localhost:8000

To stop: `docker-compose down`
To restart: `docker-compose up`

## System Requirements

1. Docker Desktop
2. Python 3.11+
3. Git
4. PowerShell or Command Prompt

## Quick Start

1. Clone the repository
```bash
git clone <repository-url>
cd credit-approval-system
```

2. Create .env file in project root
```
POSTGRES_DB=credit_approval_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
```

3. Start the application
```bash
docker-compose up --build
```

4. Run data ingestion
```bash
docker-compose exec web python manage.py ingest_data
```

The application will be available at http://localhost:8000

## Project Structure

```
credit_approval_system/
├── credit_app/                 # Main application
│   ├── models.py              # Database models
│   ├── views.py               # API views
│   ├── serializers.py         # Data serializers
│   ├── utils.py              # Business logic
│   └── management/           # Custom commands
├── customer_data.xlsx         # Initial customer data
├── loan_data.xlsx            # Initial loan data
├── docker-compose.yml        # Docker services config
├── Dockerfile                # Python application build
└── requirements.txt          # Python dependencies
```

## Data Models

1. Customer Model
   - customer_id (Auto generated)
   - first_name
   - last_name
   - age
   - phone_number (Unique)
   - monthly_salary
   - approved_limit
   - current_debt

2. Loan Model
   - loan_id (Auto generated)
   - customer (Foreign Key)
   - loan_amount
   - tenure
   - interest_rate
   - monthly_repayment
   - emis_paid_on_time
   - start_date
   - end_date

## API Endpoints

1. Register New Customer
```bash
POST /api/register/
Request:
{
    "first_name": "Test",
    "last_name": "User",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "9876543001"
}
Response:
{
    "customer_id": 310,
    "name": "Test User",
    "age": 30,
    "monthly_income": 50000,
    "approved_limit": 1800000,
    "phone_number": "9876543001"
}
```

2. Check Loan Eligibility
```bash
POST /api/check-eligibility/
Request:
{
    "customer_id": 310,
    "loan_amount": 100000,
    "interest_rate": 16,
    "tenure": 12
}
Response:
{
    "customer_id": 310,
    "approval": false,
    "interest_rate": 16.0,
    "corrected_interest_rate": 16.0,
    "tenure": 12,
    "monthly_installment": 0
}
```

3. Create New Loan
```bash
POST /api/create-loan/
Request:
{
    "customer_id": 310,
    "loan_amount": 100000,
    "interest_rate": 16,
    "tenure": 12
}
Response:
{
    "loan_id": null,
    "customer_id": 310,
    "loan_approved": false,
    "message": "Loan not approved based on eligibility criteria",
    "monthly_installment": 0
}
```

4. View Loan Details
```bash
GET /api/view-loan/5930
Response:
{
    "loan_id": 5930,
    "customer": {
        "customer_id": 14,
        "first_name": "Adaline",
        "last_name": "Diaz",
        "phone_number": "9519253076",
        "age": 65
    },
    "loan_amount": 900000.0,
    "interest_rate": 8.2,
    "monthly_installment": "15344.00",
    "tenure": 129
}
```

5. View Customer Loans
```bash
GET /api/view-loans/1
Response:
[
    {
        "loan_id": 7798,
        "loan_amount": 900000.0,
        "interest_rate": 17.92,
        "monthly_installment": "39978.00",
        "repayments_left": 94
    }
]
```

## Business Rules

1. Credit Score Calculation (0-100)
   - Past loans paid on time
   - Number of loans taken
   - Loan activity in current year
   - Loan approved volume
   - Current loans vs approved limit

2. Loan Approval Rules
   - If credit_rating > 50 approve any loan
   - If 30 < credit_rating <= 50 approve loans with interest rate > 12%
   - If 10 < credit_rating <= 30 approve loans with interest rate > 16%
   - If credit_rating <= 10 no loans approved
   - If sum of all current EMIs > 50% of monthly salary no loans approved

3. Interest Rate Correction
   - If approved interest rate does not match credit rating slab corrected rate is sent in response
   - Example If credit_rating = 20 and interest_rate = 8% corrected_interest_rate will be 16%

## Testing

1. Using PowerShell Script
```powershell
# Run comprehensive API tests
.\test_terminal.ps1
```

2. Using Python Script
```bash
# Run detailed tests with validation
python test_all_features.py
```

3. Manual Testing with curl
```bash
# Register new customer
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"first_name\":\"Test\", \"last_name\":\"User\", \"age\":30, \"monthly_income\":50000, \"phone_number\":\"9876543001\"}"

# Check eligibility
curl -X POST http://localhost:8000/api/check-eligibility/ -H "Content-Type: application/json" -d "{\"customer_id\":310, \"loan_amount\":100000, \"interest_rate\":16, \"tenure\":12}"

# Create loan
curl -X POST http://localhost:8000/api/create-loan/ -H "Content-Type: application/json" -d "{\"customer_id\":310, \"loan_amount\":100000, \"interest_rate\":16, \"tenure\":12}"

# View loan
curl http://localhost:8000/api/view-loan/5930

# View customer loans
curl http://localhost:8000/api/view-loans/1
```

## Error Handling

1. Input Validation
   - Age must be >= 18
   - Phone number must be 10 digits
   - Loan amount must be > 0
   - Interest rate must be > 0
   - Tenure must be > 0

2. Error Responses
   - 400 Bad Request Invalid input data
   - 404 Not Found Customer or loan not found
   - 409 Conflict Duplicate phone number
   - 500 Internal Server Error Unexpected errors

## Troubleshooting

1. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up --build
```

2. Data Ingestion Issues
```bash
# Check Excel files exist
ls customer_data.xlsx loan_data.xlsx

# Retry data ingestion
docker-compose exec web python manage.py ingest_data
```

3. API Connection Issues
```bash
# Check web server logs
docker-compose logs web

# Restart web server
docker-compose restart web
```

## Development

1. Making Code Changes
```bash
# Start services
docker-compose up -d

# Apply migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Run tests
docker-compose exec web python manage.py test
```

2. Accessing Database
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d credit_approval_db

# View tables
\dt

# Query data
SELECT * FROM credit_app_customer LIMIT 5;
```

