from netbox.views import generic
from . import forms, models, tables
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect


class RiskView(generic.ObjectView):
    queryset = models.Risk.objects.all()


class RiskListView(generic.ObjectListView):
    queryset = models.Risk.objects.all()
    table = tables.RiskTable
    # actions = ('add', 'export')


class RiskEditView(generic.ObjectEditView):
    queryset = models.Risk.objects.all()
    form = forms.RiskForm


class RiskDeleteView(generic.ObjectDeleteView):
    queryset = models.Risk.objects.all()


# PTRisk relation


class RiskRelationView(generic.ObjectView):
    queryset = models.RiskRelation.objects.all()


class RiskRelationListView(generic.ObjectListView):
    queryset = models.RiskRelation.objects.all()
    table = tables.RiskRelationTable


class RiskRelationEditView(generic.ObjectEditView):
    queryset = models.RiskRelation.objects.all()
    form = forms.RiskRelationForm


class RiskRelationDeleteView(generic.ObjectDeleteView):
    queryset = models.RiskRelation.objects.all()


#
# Risk assignments
#

class RiskAssignmentEditView(generic.ObjectEditView):
    queryset = models.RiskAssignment.objects.all()
    form = forms.RiskAssignmentForm
    template_name = 'risks/riskassignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            content_type = get_object_or_404(
                ContentType, pk=request.GET.get('content_type'))
            instance.object = get_object_or_404(
                content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def post(self, request, *args, **kwargs):
        form = forms.RiskAssignmentForm(request.POST)
        if form.is_valid():
            content_type_id = request.GET.get('content_type', -1)
            object_id = request.GET.get('object_id', -1)
            risk = form.cleaned_data['risk']
            qs = models.RiskAssignment.objects.filter(
                content_type=content_type_id, object_id=object_id, risk=risk.id)
            if qs.exists():
                redirect_url = request.GET.get('return_url', '/')
                return HttpResponseRedirect(redirect_url)

        return super().post(request, *args, **kwargs)


class RiskAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.RiskAssignment.objects.all()
