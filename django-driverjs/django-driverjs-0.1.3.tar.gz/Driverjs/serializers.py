from . import models

from rest_framework import serializers


class DriverSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Driver
        fields = ( 
            'className', 
            'animate', 
            'opacity', 
            'padding', 
            'allowClose', 
            'overlayClickNext', 
            'doneBtnText', 
            'closeBtnText', 
            'stageBackground', 
            'nextBtnText', 
            'prevBtnText', 
            'showButtons', 
            'keyboardControl', 
            'scrollIntoViewOptions', 
            'onHighlightStarted',
            'onHighlighted',
            'onDeselected',
            'onReset',
            'onNext',
            'onPrevious',        
        )


class DriverStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DriverStep
        fields = (
            'element', 
            'stageBackground', 
            'className', 
            'title', 
            'description', 
            'position', 
            'showButtons', 
            'doneBtnText', 
            'closeBtnText', 
            'nextBtnText', 
            'prevBtnText', 
            'onNext', 
            'onPrevious', 
        )


