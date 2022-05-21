from sys import path
from django.core.management.base import BaseCommand
import os
from pathlib import Path
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Command(BaseCommand):
    help = 'Create crud api for all installed apps'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps_list = self.get_all_installed_apps()
        apps_schemas = list(map(lambda x: x+".schema", self.apps_list))
        apps_schemas = list(map(__import__, apps_schemas))
        self.app_configs = [each.schema.app_config for each in apps_schemas]
        print("self app configs\n", self.app_configs)
        self.project_name = settings.ROOT_URLCONF.split(".")[0]

    def get_all_installed_apps(self):
        apps_list = [each_app for each_app in settings.INSTALLED_APPS if not each_app.startswith(("django.", "rest_framework", "crud_generator"))]
        return apps_list

    def create_serializer(self):
        for app_config in range(len(self.app_configs)):
            i = 0
            path = os.path.join(BASE_DIR, f"{self.app_configs[app_config]['app_name']}/api")
            if not os.path.exists(path):
                os.mkdir(path)
            with open(os.path.join(path, "serializers.py"), "a") as f:
                if i == 0:
                    f.writelines("from rest_framework import serializers")
                    f.writelines("\nimport "+f"{self.app_configs[app_config]['app_name']}"+".models as models")
                    i += 1
                for each_model in self.app_configs[app_config]["models"]:
                    f.writelines("\n\nclass "+f"{each_model}Serializer(serializers.ModelSerializer):")
                    f.writelines("\n\tclass Meta:")
                    f.writelines("\n\t\tmodel = "+f"models.{each_model}")
                    f.writelines("\n\t\tfields = '__all__'")
    
    def create_viewset(self):
        for app_config in range(len(self.app_configs)):
            i = 0
            path = os.path.join(BASE_DIR, f"{self.app_configs[app_config]['app_name']}/api")
            if not os.path.exists(path):
                os.mkdir(path)
            with open(os.path.join(path, "viewsets.py"), "a") as f:
                if i == 0:
                    f.writelines("from rest_framework import viewsets")
                    f.writelines("\nimport "+f"{self.app_configs[app_config]['app_name']}"+".api.serializers as serializers")
                    f.writelines("\nimport "+f"{self.app_configs[app_config]['app_name']}"+".models as models")
                    i += 1
                for each_model in self.app_configs[app_config]["models"]:
                    f.writelines("\n\nclass "+f"{each_model}ViewSet(viewsets.ModelViewSet):")
                    f.writelines("\n\tqueryset = "+f"models.{each_model}.objects.all()")
                    f.writelines("\n\tserializer_class = "+f"serializers.{each_model}Serializer")

    def create_routers(self):
        path = os.path.join(BASE_DIR, f"{self.project_name}")
        with open(os.path.join(path, "routers.py"), "a") as f:
            f.writelines("from rest_framework import routers\n")
            f.writelines("\n\nrouter = routers.DefaultRouter()")
            for app_config in range(len(self.app_configs)):
                f.writelines("\n\nimport "+f"{self.app_configs[app_config]['app_name']}"+".api.viewsets as "+f"{self.app_configs[app_config]['app_name']}_viewsets")                    
                for each_model in self.app_configs[app_config]["models"]:
                    f.writelines("\nrouter.register("+f"'{each_model.lower()}', {self.app_configs[app_config]['app_name']}_viewsets.{each_model}ViewSet)")
            
    def create_base_urls(self, with_ending = False):
        path = os.path.join(BASE_DIR, f"{self.project_name}/urls.py")
        f_ = open(path, "w")
        f_.close()
        with open(path, "a") as f:
            f.writelines("from django.contrib import admin\n")
            f.writelines("from django.urls import path\n")
            f.writelines("from django.urls.conf import include\n")
            f.writelines("from .routers import router\n")
            f.writelines("from rest_framework.documentation import include_docs_urls\n\n")
            f.writelines("urlpatterns = [\n")
            f.writelines("\tpath('api/admin/', admin.site.urls),")
            f.writelines("\n\t# for swagger docs")
            f.writelines("\n\tpath('api/v1/docs/', include_docs_urls(title='Project API Documentation')),")
            if with_ending:
                f.writelines("\n]")

    def create_urls(self):
        path = os.path.join(BASE_DIR, f"{self.project_name}/urls.py")
        self.create_base_urls()
        with open(path, "a") as f:
            f.writelines("\n\n\tpath('api/v1/', include(router.urls)),")
            f.writelines("\n]")


    def create_models(self):
        for app_config in range(len(self.app_configs)):
            k = 0
            j = 0
            i = 0
            for each_model in self.app_configs[app_config]["models"]:
                j = 0
                k = 0
                with open(os.path.join(BASE_DIR, f"{self.app_configs[app_config]['app_name']}/models.py"), "a") as mod_:
                    if i == 0:
                        file_ = open(os.path.join(BASE_DIR, f"{self.app_configs[app_config]['app_name']}/models.py"), "w")
                        file_.close()
                        mod_.writelines("from django.db import models")
                        if "content_type" in self.app_configs[app_config] and self.app_configs[app_config]["content_type"]:
                            mod_.writelines("\nfrom django.contrib.contenttypes.models import ContentType")
                            mod_.writelines("\nfrom django.contrib.contenttypes.fields import GenericForeignKey")
                        i += 1
                    if j == 0:
                        mod_.writelines("\n\nclass " + f"{each_model}(models.Model):")
                        j += 1
                    print("each model\n", each_model, app_config, self.app_configs[app_config]["models"])
                    for each in self.app_configs[app_config]["models"][each_model]:
                        if each == "content_type_field":
                            mod_.writelines("\n\t"+f"{self.app_configs[app_config]['models'][each_model][each]['content_type_name']} = models.ForeignKey(ContentType, on_delete=models.CASCADE)")
                            mod_.writelines("\n\t"+f"{self.app_configs[app_config]['models'][each_model][each]['object_id_name']} = models.PositiveIntegerField()")
                            mod_.writelines("\n\t"+f"{self.app_configs[app_config]['models'][each_model][each]['content_object_name']} = GenericForeignKey('{self.app_configs[app_config]['models'][each_model][each]['content_type_name']}', '{self.app_configs[app_config]['models'][each_model][each]['object_id_name']}')")
                        else:
                            datatype = self.app_configs[app_config]["models"][each_model][each]['datatype']
                            length_of_dict = len(self.app_configs[app_config]["models"][each_model][each])
                            if (datatype == "ForeignKey" or datatype == "OneToOneField" or datatype == "ManyToManyField") and length_of_dict == 2:
                                mod_.writelines("\n\t"+f"{each} = models.{datatype}({self.app_configs[app_config]['models'][each_model][each]['model']})")
                            elif (datatype == "ForeignKey" or datatype == "OneToOneField" or datatype == "ManyToManyField") and length_of_dict != 2:
                                mod_.writelines("\n\t"+f"{each} = models.{datatype}({self.app_configs[app_config]['models'][each_model][each]['model']},")
                            else:
                                mod_.writelines("\n\t"+f"{each} = models.{datatype}(")
                            k = 0
                            for inner_each in self.app_configs[app_config]["models"][each_model][each]:
                                k += 1
                                if inner_each == "datatype" or inner_each == "model":
                                    if inner_each == "datatype" and length_of_dict == 1:
                                        mod_.writelines(")")
                                    continue
                                if k==length_of_dict:
                                    mod_.writelines(f"{inner_each} = {self.app_configs[app_config]['models'][each_model][each][inner_each]})")
                                else:
                                    mod_.writelines(f"{inner_each} = {self.app_configs[app_config]['models'][each_model][each][inner_each]},")


    def handle(self, *args, **options):
        self.create_models()
        self.create_serializer()
        self.create_viewset()
        self.create_routers()
        self.create_urls()
            