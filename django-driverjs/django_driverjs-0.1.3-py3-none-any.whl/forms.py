from django import forms
from .models import Driver, DriverStep


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'slug', 'className', 'animate', 'opacity', 'padding', 'allowClose', 'overlayClickNext', 'doneBtnText', 'closeBtnText', 'stageBackground', 'nextBtnText', 'prevBtnText', 'showButtons', 'keyboardControl', 'scrollIntoViewOptions', 'onHighlightStarted', 'onHighlighted', 'onDeselected', 'onReset', 'onNext', 'onPrevious']


class DriverStepForm(forms.ModelForm):
    class Meta:
        model = DriverStep
        fields = ['element', 'stageBackground', 'className', 'title', 'description', 'showButtons', 'doneBtnText', 'closeBtnText', 'nextBtnText', 'prevBtnText', 'onNext', 'onPrevious', 'driver']


