from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Publication, Message, Profile  # Assure-toi que Profile est bien importé


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requis. Entrez une adresse email valide.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['contenu', 'image']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Quoi de neuf ?'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Écrivez votre message...'
            }),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'photo', 'ville', 'date_naissance', 'loisirs']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Parlez un peu de vous...'
            }),
            'ville': forms.TextInput(attrs={'placeholder': 'Votre ville'}),
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'loisirs': forms.TextInput(attrs={'placeholder': 'Vos loisirs (ex: lecture, sport...)'}),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
        }
