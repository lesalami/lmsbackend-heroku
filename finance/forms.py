"""
Django forms for the finance API
"""
from django import forms
from core.models import User


class UserLogin(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']
