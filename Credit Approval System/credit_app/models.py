from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(
        default=25,
        validators=[
            MinValueValidator(18, message="Age must be at least 18"),
            MaxValueValidator(100, message="Age cannot be more than 100")
        ]
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be 10 digits"
            )
        ],
        unique=True
    )
    monthly_salary = models.FloatField(
        validators=[
            MinValueValidator(0, message="Monthly salary cannot be negative")
        ]
    )
    approved_limit = models.FloatField()
    current_debt = models.FloatField(default=0)

    def clean(self):
        if not self.phone_number.isdigit():
            raise ValidationError({'phone_number': 'Phone number must have only digits'})
        
        if self.monthly_salary < 0:
            raise ValidationError({'monthly_salary': 'Monthly salary cannot be negative'})
        
        if self.current_debt < 0:
            raise ValidationError({'current_debt': 'Current debt cannot be negative'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField(
        validators=[
            MinValueValidator(0, message="Loan amount cannot be negative")
        ]
    )
    tenure = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Tenure must be at least 1 month"),
            MaxValueValidator(300, message="Tenure cannot exceed 300 months")
        ]
    )
    interest_rate = models.FloatField(
        validators=[
            MinValueValidator(0, message="Interest rate cannot be negative"),
            MaxValueValidator(100, message="Interest rate cannot exceed 100")
        ]
    )
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        if self.loan_amount <= 0:
            raise ValidationError({'loan_amount': 'Loan amount must be more than 0'})
        
        if self.monthly_repayment <= 0:
            raise ValidationError({'monthly_repayment': 'Monthly repayment must be more than 0'})
        
        if self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'End date must be after start date'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer}" 