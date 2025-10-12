from django.db import migrations

def forwards_func(apps, schema_editor):
    """
    Migrate existing Loan, Deduction, and LoanRepayment records to the new
    FinancialTransaction model.
    """
    Loan = apps.get_model('users', 'Loan')
    Deduction = apps.get_model('users', 'Deduction')
    LoanRepayment = apps.get_model('users', 'LoanRepayment')
    FinancialTransaction = apps.get_model('users', 'FinancialTransaction')

    for loan in Loan.objects.all():
        FinancialTransaction.objects.create(
            staff=loan.staff,
            transaction_type='loan',
            amount=loan.amount,
            date=loan.date_issued,
            description=loan.notes or "Loan issued",
            related_loan=loan
        )

    for deduction in Deduction.objects.all():
        FinancialTransaction.objects.create(
            staff=deduction.staff,
            transaction_type='deduction',
            amount=deduction.amount,
            date=deduction.date,
            description=deduction.reason
        )

    for repayment in LoanRepayment.objects.all():
        FinancialTransaction.objects.create(
            staff=repayment.loan.staff,
            transaction_type='repayment',
            amount=repayment.amount,
            date=repayment.date_paid,
            description=f"Repayment for loan #{repayment.loan.id}",
            related_loan=repayment.loan
        )

def reverse_func(apps, schema_editor):
    """
    Reverse the data migration. This will delete all FinancialTransaction
    records, but it will not restore the old models, as they will be
    removed in a subsequent migration.
    """
    FinancialTransaction = apps.get_model('users', 'FinancialTransaction')
    FinancialTransaction.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_financialtransaction'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]