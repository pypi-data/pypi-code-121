from django.contrib import admin
from django import forms
from .models import Driver, DriverStep
from django_summernote.widgets import SummernoteWidget
from django_ace import AceWidget

class DriverStepAdminForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())
    onNext = forms.CharField(required=False,widget=AceWidget(mode='javascript'))
    onPrevious = forms.CharField(required=False,widget=AceWidget(mode='javascript'))

    class Meta:
        model = DriverStep
        fields = '__all__'

 
class DriverStepInline(admin.TabularInline):
    model = DriverStep
    form = DriverStepAdminForm
    extra = 1

class DriverAdminForm(forms.ModelForm):
    onHighlightStarted = forms.CharField(required=False,widget=AceWidget(mode='javascript', width="100%"))
    onHighlighted = forms.CharField(required=False,widget=AceWidget(mode='javascript',width="100%"))
    onDeselected = forms.CharField(required=False,widget=AceWidget(mode='javascript',width="100%"))
    onReset = forms.CharField(required=False,widget=AceWidget(mode='javascript',width="100%"))
    onNext = forms.CharField(required=False,widget=AceWidget(mode='javascript',width="100%"))
    onPrevious = forms.CharField(required=False,widget=AceWidget(mode='javascript',width="100%"))

    class Meta:
        model = Driver
        fields = '__all__'


class DriverAdmin(admin.ModelAdmin):
    form = DriverAdminForm
    inlines = [DriverStepInline,]
    list_filter = ('is_active',)
    list_display = ['name', 'slug','is_active' ,'className', 'animate', 'opacity', 'padding', 'allowClose', 'overlayClickNext', 'doneBtnText', 'closeBtnText', 'stageBackground', 'nextBtnText', 'prevBtnText', 'showButtons', 'keyboardControl', ]
    # readonly_fields = ['name', 'slug', 'created', 'last_updated', 'className', 'animate', 'opacity', 'padding', 'allowClose', 'overlayClickNext', 'doneBtnText', 'closeBtnText', 'stageBackground', 'nextBtnText', 'prevBtnText', 'showButtons', 'keyboardControl', 'scrollIntoViewOptions', 'onHighlightStarted', 'onHighlighted', 'onDeselected', 'onReset', 'onNext', 'onPrevious']

    def get_queryset(self, request):
        return Driver.objects_all.all()

admin.site.register(Driver, DriverAdmin)


