from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Booking
from organizer.models import Package

class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        label="First name:",
        max_length= 100,
        widget= forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John'
        })
    )
    
    last_name = forms.CharField(
        required=True,
        label="Last name:",
        max_length=100,
        widget= forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder': 'Doe',
        })
    )
    
    username = forms.EmailField(
        required=True,
        label="Email:",
        max_length= 100,
        widget= forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'johndoe@gmail.com'
        })
    )

    password1 = forms.CharField(
        required=True,
        label="Password:",
        widget=forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder': '•••••••••',
        })
    )
    
    password2 = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '•••••••••',
        })
    )
    
    
    class Meta:
        model = User    
        fields = ['first_name', 'last_name', 'username', 'password1', 'password2']
        
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        email = cleaned_data.get("username")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match")
            
        if email and User.objects.filter(email=email).exists():
            self.add_error("username", "A user with this email already exists.")

        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["username"]
        user.password = make_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    username = forms.EmailField(
        required=True,
        label="Email:",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'johndoe@gmail.com'
        })
    )
    password = forms.CharField(
        required=True,
        label="Password:",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '•••••••••'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)  # Check if user exists
                
                if not user.is_active:
                    cleaned_data["inactive_user"] = user  # Store inactive user for the view
                    return cleaned_data  # ✅ Return without authentication

                authenticated_user = authenticate(username=user.username, password=password)
                if authenticated_user is None:
                    raise forms.ValidationError("Invalid email or password.")

                cleaned_data["user"] = authenticated_user  # Store the authenticated user

            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data
    
class BookingForm(forms.ModelForm):
    wedding_date = forms.DateField(
        required=True,
        label="Pick your wedding date:",
        widget= forms.DateInput(attrs={
            'class': 'form-control',
            'type':'date',
        }),
        
    )
    
    package = forms.ModelChoiceField(
        required=True,
        label="Select package: ",
        queryset= Package.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    class Meta:
        model = Booking
        fields = ['wedding_date', 'package']
