from django import forms
from django.contrib.auth.models import User
from .models import Customer, Staff, Loan, Deduction, Leave, LoanRepayment

class StaffForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Staff
        fields = ['role', 'phone_number', 'salary']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['amount', 'date', 'reason', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'leave_type', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanRepayment
        fields = ['amount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(required=False)

    class Meta:
        model = Customer
        fields = ['phone_number', 'address', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        # The user instance is created or updated separately in the view
        customer = super().save(commit=False)

        # We handle the user fields here
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')

        if self.instance and self.instance.pk and self.instance.user:
            # Update existing user
            user = self.instance.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = email or f'{first_name}_{last_name}' # Ensure username is unique
        else:
            # This form is not responsible for creating the User object itself
            # The view will handle User creation.
            pass

        if commit:
            if 'user' in locals():
                user.save()
            customer.save()

        return customer
