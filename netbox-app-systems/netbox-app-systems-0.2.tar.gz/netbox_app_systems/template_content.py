from extras.plugins import PluginTemplateExtension
from django.contrib.contenttypes.models import ContentType
from .models import AppSystemAssignment
# from netbox.models.


class AppSystemVMPanel(PluginTemplateExtension):
    model = 'virtualization.virtualmachine'
    # model = 'dcim.device'

    def left_page(self):
        vm = self.context['object']
        content_type_id = ContentType.objects.get_for_model(model=vm).id
        app_systems = AppSystemAssignment.objects.filter(
            object_id=vm.id, content_type=content_type_id)
        # print(vars(AppSystem_ass))
        # print(AppSystem_ass)
        AppSystems = []
        for s in app_systems:
            AppSystems.append({
                'id': s.id,
                'app_system': s.app_system})
            # print(s.__dict__)

        print(AppSystems)
        return self.render('netbox_app_systems/app_system_panel.html', extra_context={
            'app_systems': AppSystems
        })


class AppSystemDevicePanel(PluginTemplateExtension):
    model = 'dcim.device'

    def left_page(self):
        vm = self.context['object']
        content_type_id = ContentType.objects.get_for_model(model=vm).id
        app_systems = AppSystemAssignment.objects.filter(
            object_id=vm.id, content_type=content_type_id)
        AppSystems = []
        for s in app_systems:
            AppSystems.append({
                'id': s.id,
                'app_system': s.app_system})
            # print(s.__dict__)

        return self.render('netbox_app_systems/app_system_panel.html', extra_context={
            'app_systems': AppSystems
        })


template_extensions = [AppSystemVMPanel, AppSystemDevicePanel]
