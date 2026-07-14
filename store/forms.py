from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Review



# ---------------- REGISTER FORM ----------------

class RegisterForm(UserCreationForm):

    class Meta:

        model = User

        fields = [
            'username',
            'password1',
            'password2'
        ]



# ---------------- REVIEW FORM ----------------

class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = [
            'rating',
            'comment'
        ]


        widgets = {

            'rating': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),


            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Write your review'
                }
            )

        }