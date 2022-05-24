
from django import forms

from captcha.fields import ReCaptchaField

from reviews.models import Review


class ReviewForm(forms.ModelForm):

    captcha = ReCaptchaField()

    class Meta:
        model = Review
        fields = ['name', 'text', 'rating', 'photo']
