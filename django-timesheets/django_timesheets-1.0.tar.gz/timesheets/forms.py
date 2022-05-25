from dataclasses import field, fields
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import DateField, ModelForm
from .models import Master_db
from django.forms import formset_factory
from django.forms.models import inlineformset_factory, modelform_factory, modelformset_factory



class DateInput(forms.DateInput):
	input_type = 'date'

class Masterdb(ModelForm):
    class Meta:
        model = Master_db
        fields = ('name','client','project','date','description','hours','category','billable')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', }),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type':'date','class':'form-control', 'id':'date_id'}),
            'description': forms.TextInput(attrs={'class': 'form-control',}),
            'hours': forms.NumberInput(attrs={'class': 'form-control','id':'id_hours','style': 'width:7ch'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id':'id_category', 'onchange': 'updatehours()'}),
            'billable': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Text goes here', 'rows': '4', 'cols': '10', 'id':'text'}),
        }

# Masterdbformset = inlineformset_factory(
#     Master_db, Masterdb, can_delete=True, extra = 0
# )

        
      
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','password1','password2']


    # widgets = {
    #         'username':forms.TextInput(attrs={'class':'center','placeholder': 'Enter Name'}),
    #         'password1': forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter pass'}),
    #         'password2':forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Confirm Passoword'})
    #     }
     