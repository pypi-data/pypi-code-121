import datetime
from django import forms

# https://stackoverflow.com/questions/3367091/whats-the-cleanest-simplest-to-get-running-datepicker-in-django


class DateInput(forms.DateInput):
    input_type = 'date'


class AppointmentForm(forms.Form):
    name = forms.CharField(
        label='', max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '성함', 'class': 'form-control'})
    )
    phone = forms.CharField(
        label='', max_length=20,
        widget=forms.TextInput(attrs={'placeholder': '연락처', 'class': 'form-control'})
    )
    date = forms.DateField(
        label='',
        # https://docs.djangoproject.com/en/3.2/ref/forms/fields/
        initial=datetime.date.today,
        widget=DateInput(attrs={'placeholder': '예약일', 'class': 'form-control'})
    )
    message = forms.CharField(
        label='',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': '상담 내용',
                                     'class': 'form-control',
                                     'rows': '4'}))

    class Meta:
        widgets = {
            'date': DateInput(),
        }
