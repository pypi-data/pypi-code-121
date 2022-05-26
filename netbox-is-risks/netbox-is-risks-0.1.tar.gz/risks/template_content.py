from extras.plugins import PluginTemplateExtension
from django.contrib.contenttypes.models import ContentType
from risks.models import RiskAssignment


class RiskVMPanel(PluginTemplateExtension):
    model = 'virtualization.virtualmachine'

    def right_page(self):
        vm = self.context['object']
        content_type_id = ContentType.objects.get_for_model(model=vm).id
        risk_ass = RiskAssignment.objects.filter(
            object_id=vm.id, content_type=content_type_id)
        risks = []
        for r in risk_ass:
            risks.append({
                'assignment_id': r.id,
                'name': r.risk,
                'rel': r.relation.name
            })

        return self.render('risks/risk_panel.html', extra_context={
            'risks': risks
        })


class RiskDevicePanel(PluginTemplateExtension):
    model = 'dcim.device'

    def right_page(self):
        device = self.context['object']
        content_type_id = ContentType.objects.get_for_model(model=device).id
        risk_ass = RiskAssignment.objects.filter(
            object_id=device.id, content_type=content_type_id)
        risks = []
        for r in risk_ass:
            risks.append({
                'assignment_id': r.id,
                'name': r.risk,
                'rel': r.relation.name
            })

        return self.render('risks/risk_panel.html', extra_context={
            'risks': risks
        })


template_extensions = [RiskVMPanel, RiskDevicePanel]
