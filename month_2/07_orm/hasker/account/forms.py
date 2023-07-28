from django import forms
from django.contrib.auth.models import User

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_repeat = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    def clean_password_repeat(self):
        clean_data = self.cleaned_data

        if clean_data['password'] != clean_data['password_repeat']:
            raise forms.ValidationError('Passwords do not match!')

        return clean_data['password_repeat']

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already used!')

        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        """Forbid to use email of other user."""
        email = self.cleaned_data['email']
        query = User.objects.exclude(id=self.instance.id).filter(email=email)

        if query.exists():
            raise forms.ValidationError('Email already used!')

        return email
