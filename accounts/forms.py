from django import forms
from .models import *

#~ import datetime, pytz

class UserForm(forms.ModelForm):
    
    first_name = forms.CharField(required=True, widget=forms.TextInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
    last_name  = forms.CharField(required=True, widget=forms.TextInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
    username   = forms.CharField(required=True, widget=forms.TextInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
                    
    old_password   = forms.CharField(required=True, widget=forms.PasswordInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
    

    new_password   = forms.CharField(required=False, widget=forms.PasswordInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))

    verify_password   = forms.CharField(required=False, widget=forms.PasswordInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
                    
    gender     = forms.ChoiceField( choices= User.GENDER, widget=forms.RadioSelect(), )
    
    #~ birth_date = forms.CharField(widget=forms.TextInput(attrs={'class' : 'date-picker form-control col-md-7 col-xs-12'}))
    
    email   = forms.EmailField(required=False, widget=forms.TextInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
    webpage_url   = forms.URLField(required=False, widget=forms.TextInput(
                    attrs={'class' : 'form-control col-md-7 col-xs-12'}
                    ))
    #~ bio        = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control col-md-7 col-xs-12'}))
    avatar        = forms.ImageField(widget=forms.FileInput(), required=False)
    
    class Meta:
        model = User
        fields = "__all__" 
        exclude = ('is_active', 'is_superuser', 'date_joined', 'password')
