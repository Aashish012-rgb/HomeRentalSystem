from django import forms 
from .models import home, Property
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class homeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs["class"] = "form-control"

    class Meta:
        model = home
        fields =['text','photo']


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            if "password" in field_name:
                field.widget.attrs["autocomplete"] = "new-password"

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Property
        fields = ['title','description','price','location', 'property_type','image']
