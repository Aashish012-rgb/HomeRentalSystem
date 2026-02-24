from django import forms 
from .models import home
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class homeForm(forms.ModelForm):
    class Meta:
        model = home
        fields =['text','photo']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')