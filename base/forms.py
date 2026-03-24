from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User
import re

EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if not re.match(EMAIL_REGEX, email):
                raise forms.ValidationError('Enter a valid email address.')
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError('A user with that email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            if User.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError('A user with that username already exists.')
        return username


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']