from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('credit_app', '0002_alter_customer_age_alter_customer_approved_limit_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - cleanup
            """
            DELETE FROM credit_app_loan WHERE customer_id NOT IN (SELECT customer_id FROM credit_app_customer);
            DELETE FROM credit_app_customer WHERE age < 18 OR age > 100;
            UPDATE credit_app_customer SET current_debt = 0 WHERE current_debt IS NULL;
            """,
            # Reverse SQL - no action needed
            """
            SELECT 1;
            """
        ),
    ] 