from dataclasses import field, fields
from pyexpat import model
from rest_framework import serializers
from timesheets.models import Admin,  Client, Master_db, Project, Master_db, Users,Category

class ClientSerializers(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('client_id', 'client_name')

class UsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('userid', 'name')
    
class AdminSerializers(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ('admin_id','name')

class MasterdbSerializers(serializers.ModelSerializer):
    class Meta:
        model = Master_db
        fields = ('timesheetid','billable','date','hours','description','name', 'client','project', 'category')

class ProjectSerializers(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('project_id','project_name')

class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_id','category_name')