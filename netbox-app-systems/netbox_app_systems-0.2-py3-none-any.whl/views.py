from netbox.views import generic
from . import forms, models, tables
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect


class AppSystemView(generic.ObjectView):
    queryset = models.AppSystem.objects.all()

    def get_extra_context(self, request, instance):
        app_system_assignments = models.AppSystemAssignment.objects.filter(
            app_system=instance)
        assignments_table = tables.AppSystemAssignmentTable(
            app_system_assignments)
        assignments_table.columns.hide('app_system')
        assignments_table.configure(request)
        return {
            'assignments_table': assignments_table
        }


class AppSystemListView(generic.ObjectListView):
    queryset = models.AppSystem.objects.all()
    table = tables.AppSystemTable


class AppSystemEditView(generic.ObjectEditView):
    queryset = models.AppSystem.objects.all()
    form = forms.AppSystemForm


class AppSystemDeleteView(generic.ObjectDeleteView):
    queryset = models.AppSystem.objects.all()


class AppSystemAssignmentEditView(generic.ObjectEditView):
    queryset = models.AppSystemAssignment.objects.all()
    form = forms.AppSystemAssignmentForm
    template_name = 'netbox_app_systems/app_system_assignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            content_type = get_object_or_404(
                ContentType, pk=request.GET.get('content_type'))
            instance.object = get_object_or_404(
                content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def post(self, request, *args, **kwargs):
        form = forms.AppSystemAssignmentForm(request.POST)
        if form.is_valid():
            content_type_id = request.GET.get('content_type', -1)
            object_id = request.GET.get('object_id', -1)
            s = form.cleaned_data['app_system']
            qs = models.AppSystemAssignment.objects.filter(
                content_type=content_type_id, object_id=object_id, app_system=s.id)
            if qs.exists():
                redirect_url = request.GET.get('return_url', '/')
                return HttpResponseRedirect(redirect_url)

        return super().post(request, *args, **kwargs)


class AppSystemAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.AppSystemAssignment.objects.all()
