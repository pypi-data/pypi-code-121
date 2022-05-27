import json
from multiprocessing import Manager
from django.urls import reverse
from django.conf import settings
from django.db import models as models
 
from django.utils.safestring import mark_safe


class DriverManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Driver(models.Model):

    # Fields
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    is_active = models.BooleanField(default=True)

    className = models.TextField(help_text="className to wrap driver.js popover", blank=True, null=True)
    animate = models.BooleanField(default=True,help_text="Whether to animate or not")
    opacity = models.FloatField(default=0.75,help_text="Background opacity (0 means only popovers and without overlay)")
    padding = models.IntegerField(default=10,help_text="Distance of element from around the edges")
    allowClose = models.BooleanField(default=True,help_text="Whether the click on overlay should close or not")
    overlayClickNext = models.BooleanField(help_text="Whether the click on overlay should move next",default=False)
    doneBtnText = models.CharField(max_length=200,help_text="Text on the final button",blank=True,null=True)
    closeBtnText = models.CharField(max_length=200,help_text="Text on the close button for this step",blank=True,null=True)
    stageBackground = models.CharField(max_length=200,help_text="Background color for the staged behind highlighted element",blank=True,null=True)
    nextBtnText = models.CharField(max_length=200,help_text="Next button text for this step",blank=True,null=True)
    prevBtnText = models.CharField(max_length=200,help_text="Previous button text for this step",blank=True,null=True)
    showButtons = models.BooleanField(help_text="Do not show control buttons in footer",default=False)
    keyboardControl = models.BooleanField(help_text="Allow controlling through keyboard (escape to close, arrow keys to move)",default=True)
    scrollIntoViewOptions = models.TextField(help_text="We use `scrollIntoView()` when possible, pass here the options for it if you want any - dictionary {}",blank=True,null=True)
    onHighlightStarted = models.TextField(help_text="Called when element is about to be highlighted",blank=True,null=True)
    onHighlighted = models.TextField(help_text="Called when element is fully highlighted",blank=True,null=True)
    onDeselected = models.TextField(help_text="Called when element has been deselected",blank=True,null=True)
    onReset = models.TextField(help_text="Called when overlay is about to be cleared",blank=True,null=True)
    onNext = models.TextField(help_text="Called when moving to next step on any step",blank=True,null=True)
    onPrevious = models.TextField(help_text="Called when moving to previous step on any step",blank=True,null=True)

    # Managers
    objects = DriverManager()
    objects_all = models.Manager()


    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return u'%s' % self.slug
    
POSITION_CHOICES=(
    ('left', 'left'),
    ('left-center', 'left-center'),
    ('left-bottom', 'left-bottom'),
    ('top', 'top'),
    ('top-center', 'top-center'),
    ('top-right', 'top-right'),
    ('right', 'right'),
    ('right-center', 'right-center'),
    ('right-bottom', 'right-bottom'),
    ('bottom', 'bottom'),
    ('bottom-center', 'bottom-center'),
    ('bottom-right', 'bottom-right'),
    ('mid-center', 'mid-center'),
) 
class DriverStep(models.Model):

    # Fields
    step_nbr = models.IntegerField()

    element = models.TextField(help_text="Query selector string or Node to be highlighted")
    stageBackground = models.TextField(help_text="Background color for the staged behind highlighted element",blank=True,null=True)
    className = models.TextField(help_text="className to wrap this specific step popover in addition to the general className in Driver options", blank=True, null=True)
    title = models.TextField(help_text="Title on the popover", blank=True, null=True)
    description = models.TextField(help_text="Body of the popover", blank=True, null=True)
    position = models.CharField(max_length=200,help_text="Position of the popover",blank=True,null=True, choices=POSITION_CHOICES)
    showButtons = models.BooleanField(help_text="Do not show control buttons in footer",default=False)
    doneBtnText = models.CharField(max_length=200,help_text="Text on the final button",blank=True,null=True)
    closeBtnText = models.CharField(max_length=200,help_text="Text on the close button for this step",blank=True,null=True)
    nextBtnText = models.CharField(max_length=200,help_text="Next button text for this step",blank=True,null=True)
    prevBtnText = models.CharField(max_length=200,help_text="Previous button text for this step",blank=True,null=True)
    onNext = models.TextField(help_text="Called when moving to next step from current step",blank=True,null=True)
    onPrevious = models.TextField(help_text="Called when moving to previous step from current step",blank=True,null=True)

    # Relationship Fields
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='driversteps') 

    class Meta:
        ordering = ('step_nbr',)
        unique_together = ('driver', 'step_nbr')

    def __str__(self):
        return u'%s' % self.pk
 
