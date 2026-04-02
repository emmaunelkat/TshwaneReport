"""
reports/forms.py
────────────────
FaultReportForm  – rendered on the 3-step submission screen.
"""

from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import FaultReport, UserProfile


class FaultReportForm(forms.ModelForm):

    # Hidden fields populated by JavaScript (GPS capture) or manual entry
    latitude  = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    address   = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model  = FaultReport
        fields = [
            'category',
            'latitude',
            'longitude',
            'address',
            'description',
            'photo',
            'language',
            'simplified_mode',
        ]
        widgets = {
            'category': forms.HiddenInput(),   # set by URL parameter
            'language': forms.HiddenInput(),   # set by session
            'simplified_mode': forms.HiddenInput(),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Optional: Describe the fault in more detail...',
                'class': 'form-control',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'environment',   # opens rear camera on mobile
            }),
        }
        labels = {
            'description': 'Add a description (optional)',
            'photo':       'Add a photo (helps us respond faster) – OPTIONAL',
        }


class UserRegistrationForm(forms.Form):
    """
    Form for user registration with ID number validation.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (must end with @gmail.com)'
        })
    )
    id_number = forms.CharField(
        max_length=13,
        min_length=13,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{13}$',
                message='ID number must be exactly 13 digits.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID Number (13 digits)'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError('Email must end with @gmail.com')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if UserProfile.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError('This ID number is already registered.')
        return id_number
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data


class UserLoginForm(forms.Form):
    """
    Form for user login using ID number and password.
    """
    id_number = forms.CharField(
        max_length=13,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ID Number (13 digits)'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )