from collections import UserList
from dataclasses import fields
import datetime
from doctest import master
from http import client
from os import times
from pyexpat import model
from pyexpat.errors import messages
from unicodedata import category, name
from unittest import result
from urllib import response
from xmlrpc.client import FastMarshaller
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy 
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Now
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from numpy import singlecomplex, where
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from timesheets.forms import Masterdb, CreateUserForm
from timesheets.models import Master_db
from rest_framework import viewsets, filters, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response 


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import generic
import xlwt




from timesheets.models import Admin, Client, Project, Master_db, Users
from timesheets.serializers import AdminSerializers, ClientSerializers, ProjectSerializers, UsersSerializers, MasterdbSerializers


from .forms import Masterdb
from django.views.generic.edit import CreateView, UpdateView
# Create your views here.

@csrf_exempt

def clientapi(request, id = 0):
    if request.method == 'GET':
        clients = Client.objects.all()
        clients_serializer = ClientSerializers(clients, many = True)
        return JsonResponse(clients_serializer.data, safe = False)
    elif request.method == 'POST':
       client_data =  JSONParser().parse(request)
       clients_serializer = ClientSerializers(data = client_data)
       if clients_serializer.is_valid():
           clients_serializer.save()
           return JsonResponse("success.", safe= False)
    elif request.method == "PUT":
        client_data = JSONParser().parse(request)
        client = Client.objects.get(client_id  = client_data['client_id'])
        clients_serializer = ClientSerializers(client, data = client_data)
        if clients_serializer.is_valid():
            clients_serializer.save()
            return JsonResponse("Updated.", safe = False)
        return JsonResponse("Update failed.")
    elif request.method == "DELETE":
        clients = Client.objects.get(client_id = id)
        clients.delete()
        return JsonResponse("Deleted Successfully", safe = False)

@csrf_exempt

def Userapi(request, id = 0):
    if request.method == 'GET':
        users = Users.objects.all()
        users_serializers = UsersSerializers(users, many = True)
        return JsonResponse(users_serializers.data, safe = False)
    elif request.method=='POST':
        users_data = JSONParser().parse(request)
        users_serializers = UsersSerializers(data = users_data)
        if users_serializers.is_valid():
            users_serializers.save()
            return JsonResponse("success", safe = False)
    elif request.method=='PUT':
        users_data = JSONParser().parse(request)
        users = Users.objects.get(userid = users_data['userid'])
        users_serializers = UsersSerializers(users, data = users_data)
        if users_serializers.is_valid():
            users_serializers.save()
            return JsonResponse("Updated", safe = False)
        return JsonResponse("Update failed")
    elif request.method=='DELETE':
        users = Users.objects.get(userid = id)
        users.delete()
        return JsonResponse("Deleted Success", safe = False)       



@csrf_exempt

def Adminapi(request, id = 0):
    if request.method == 'GET':
        admins = Admin.objects.all()
        admin_serializers = AdminSerializers(admins, many = True)
        return JsonResponse(admin_serializers.data, safe = False)
    elif request.method=='POST':
        admin_data = JSONParser().parse(request)
        admin_serializers =AdminSerializers(data =admin_data)
        if admin_serializers.is_valid():
            admin_serializers.save()
            return JsonResponse("success", safe = False)
    elif request.method=='PUT':
        admin_data = JSONParser().parse(request)
        admins = Admin.objects.get(userid = admin_data['admin_id'])
        admin_serializers = AdminSerializers(admins, data = admin_data)
        if admin_serializers.is_valid():
            admin_serializers.save()
            return JsonResponse("Updated", safe = False)
        return JsonResponse("Update failed")
    elif request.method=='DELETE':
        admins = Admin.objects.get(userid = id)
        admins.delete()
        return JsonResponse("Deleted Success", safe = False)       



@csrf_exempt

def Projectapi(request, id = 0):
    if request.method == 'GET':
        projects = Project.objects.all()
        project_serializers = ProjectSerializers(projects, many = True)
        return JsonResponse(project_serializers.data, safe = False)
    elif request.method=='POST':
        project_data = JSONParser().parse(request)
        project_serializers =ProjectSerializers(data = project_data)
        if project_serializers.is_valid():
            project_serializers.save()
            return JsonResponse("success", safe = False)
    elif request.method=='PUT':
        project_data = JSONParser().parse(request)
        projects = Project.objects.get(userid = project_data['project_id'])
        project_serializers = ProjectSerializers(projects, data = project_data)
        if project_serializers.is_valid():
            project_serializers.save()
            return JsonResponse("Updated", safe = False)
        return JsonResponse("Update failed")
    elif request.method=='DELETE':
        projects = Project.objects.get(userid = id)
        projects.delete()
        return JsonResponse("Deleted Success", safe = False)     

           

@csrf_exempt

def Masterdbapi(request, id = 0):
    if request.method == 'GET':
        entries = Master_db.objects.all()
        masterdb_serializers = MasterdbSerializers(entries, many = True)
        return JsonResponse(masterdb_serializers.data, safe = False)
    elif request.method=='POST':
        masterdb_data = JSONParser().parse(request)
        masterdb_serializers = MasterdbSerializers(data = masterdb_data)
        if masterdb_serializers.is_valid():
            masterdb_serializers.save()
            return JsonResponse("success", safe = False)
    elif request.method=='PUT':
        masterdb_data = JSONParser().parse(request)
        entries = Master_db.objects.get(userid = masterdb_data['timesheetid'])
        masterdb_serializers = MasterdbSerializers(entries, data = masterdb_data)
        if masterdb_serializers.is_valid():
            masterdb_serializers.save()
            return JsonResponse("Updated", safe = False)
        return JsonResponse("Update failed")
    elif request.method=='DELETE':
        entries = Master_db.objects.get(userid = id)
        category.delete()
        return JsonResponse("Deleted Success", safe = False)      

class CreateEntry(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Master_db.objects.all()
    serializer_class = MasterdbSerializers

class RetriveEntry(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Master_db.objects.all()
    serializer_class = MasterdbSerializers

class UpdateEntry(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Master_db.objects.all()
    serializer_class = MasterdbSerializers

class DeleteEntry(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Master_db.objects.all()
    serializer_class = MasterdbSerializers


class addEntry(CreateView):
    model = Master_db
    template_name = 'timesheet.html'
    form_class = Masterdb


def addEntry(request):
    

    # name = request.user
    # results = Master_db.objects.filter(name = name).order_by('-id')[:5]
    

    name = request.user
    results = Master_db.objects.filter(name = name).order_by('-timesheetid')[:5]
    
    if request.method =="POST":
        form = Masterdb(request.POST)

        
            
        if form.is_valid():
            masterdb_item = form.save(commit = False)
            masterdb_item.save()
            form = Masterdb()
            messages.success(request, 'Entry Saved Successfully')



    else:
        form  = Masterdb()
    
   
    return render (request, 'timesheet.html', {'form': form,'addEntry':results})


def registerpage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()

    context = {'form': form}
    return render (request, 'register.html', context)


class register(CreateView):
    model = User 
    template_name = 'register.html'
    form_class = CreateUserForm

from django.contrib import messages
def loginpage(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
    
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('userentry')
        else:
            messages.success(request, 'Incorrect Username or Password')
            return render(request,'login.html')

    context = {}
    return render (request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('loginpage')

def newentry(request):
    return render(request, 'home.html')


def preventries(request):

    return render(request, 'previous.html')


class getData(generic.UpdateView):

     
        template_name = 'previous.html'
        form_class = Masterdb
        fields = ['billable','date','hours','description','name', 'client','project', 'category']
        success_url = reverse_lazy('newentry')

from django.utils import timezone
from datetime import date, timedelta, datetime
@login_required
def get_entry(request):
    name = request.user
    results = Master_db.objects.filter(name = name).order_by('-id')[:5]
    return render(request,'timesheet.html',{'get_entry':results})


def updatentry(request): 
       
            #results = Master_db.objects.all()
        time_threshold = datetime.now() - timedelta(days=14)
        now = timezone.now()
        results = Master_db.objects.filter(date__gt = time_threshold).order_by("-timesheetid")
        # results = Master_db.objects.aggregate(
        #     last_14_days = models.Count('timesheetid',filter=models.Q(date=(now - timedelta(days=14)).date())),
        # )
        # status_filter = UserFilter(request.GET, queryset=results)
        return render(request, "previous.html",{'updatentry':results})

# def viewentry(request):
#     results = Master_db.objects.filter(Now())
#     return render(request, "timesheet.html", {'viewentry':results})
        

# def editentry(request,id): 

#         results = Master_db.objects.get(timesheetid = id)
#         return render(request, "edit.html",{'Master_db':results})

def editentry(request,id):

    entries = Master_db.objects.get(timesheetid = id)
    form = Masterdb(instance=entries)

    if request.method =="POST":
        form = Masterdb(request.POST, instance=entries)
        if form.is_valid():
            form.save()
            return redirect('preventry')


    context = {'form':form }
    return render(request, 'edit.html', context)


def deletentry(request, id):
    entries = Master_db.objects.get(timesheetid = id)
    entries.delete()
    return render(request, 'delete.html')

def homepage(request):
    return render(request, 'page1.html')


def export_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename = Master_db'+ \
        str(datetime.datetime.now())+'.xls'
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('Master_db')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True


    columns = ['billable','date','hours','description','name', 'client_name','project', 'category']

    for col_num in range(len(columns)):
    
        ws.write(row_num,col_num,columns[col_num], font_style)

    font_style = xlwt.XFStyle()


    rows = Master_db.objects.values_list(
        'billable','date','hours','description','name', 'client' ,'project', 'category')
    
    for row in rows:
        row_num+=1

        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]), font_style)
    wb.save(response)

    return response


def TableView( request):
  

    if request.method =="POST":
        form = Masterdb(request.POST)

        
            
        if form.is_valid():
            masterdb_item = form.save(commit = False)
            masterdb_item.save()
            form = Masterdb()
            messages.success(request, 'Entry Saved Successfully')



    else:
        form  = Masterdb()
    
   
    return render (request, 'tableview.html', {'form': form})

def viewEntries(request):
    if User.username == Master_db.name:
        name = Master_db.name
        results = Master_db.objects.filter(name = name).order_by()[:5]
        return render(request, "timesheet.html", {results})

from django.forms import *


    # context ={}
  
    # # creating a formset
    # sample_form_set = formset_factory(Masterdb)
    # formset = sample_form_set(data=request.POST)

    # if request.method == 'POST':
      
    #     masterdb_item = formset.save(commit = False)
       
    #     masterdb_item.save()
    #     formset = Mas
    # 
    #   terdb()

def get(request):
    context = {}
    # context['formset']= formset
    # return render(request, "tableview.html", context)
    # creating a formset
    sample_formset = formset_factory(Masterdb)
    formset = sample_formset(request.POST)
      
    #Add the formset to context dictionary
    context['formset']= formset
    return render(request, "tableview.html", context)
        # sample_form_set = sample_form_set_factory()
        
        
        # if request.method=="POST":
        
        #     formset = sample_form_set(request.POST, queryset = Master_db.objects.none())
        #     if formset.is_valid():
        #         masterdb_item = formset.save(commit = False)
        #         masterdb_item.save()
        #         formset = Masterdb()
        #         messages.success(request, 'Entry Saved Successfully')

        # context = {
        #     'sample_form' : formset,
        # }
        
        # return render(request, 'tableview.html', context)

        

def index(request):
    masterdb_items = Master_db.objects.all()
    extra_forms = 1
    DrinkFormSet =formset_factory(  extra=extra_forms, form=Masterdb)
    
        # if 'additems' in request.POST and request.POST['additems'] == 'true':
        #     formset_dictionary_copy = request.POST.copy()
        #     formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) + extra_forms
        #     formset = DrinkFormSet(formset_dictionary_copy)
        # else:
    formset = DrinkFormSet(request.POST)
    if formset.is_valid():
                
                #formset.save()
                # formset = Master_db
                messages.success(request, 'Entry Saved Successfully')

    else:
        formset = DrinkFormSet()
    return render(request,'tableview.html',{'formset':formset})

# from .forms import Masterdbformset

# def addmore(request):
  
#     formset = Masterdbformset(request.POST or None)
    
#     if request.method =="POST":
#         if formset.is_valid():
            
#             formset.save()
#             return redirect("addmore")

#     context = {
#         'formset':'formset'
#     }
#     return render(request, "tablevew.html", context)


from django.shortcuts import render

  
# importing formset_factory
from django.forms import formset_factory
  
def test1(request):
    context ={}
  
    # creating a formset and 5 instances of GeeksForm
    GeeksFormSet = formset_factory(Masterdb, extra = 1)
    formset = GeeksFormSet(request.POST or None)
    print("Hello")
      
    # print formset data if it is valid
    if formset.is_valid():
        for form in formset:
            print(form.cleaned_data)
              
    # Add the formset to context dictionary
    context['formset']= formset
    return render(request, "tableview.html", context)


from django.shortcuts import render


# importing formset_factory
from django.forms import formset_factory

def formset_view(request):
	context ={}

	# creating a formset
	GeeksFormSet = modelformset_factory(Master_db, form=Masterdb)
	formset = GeeksFormSet()
	
	# Add the formset to context dictionary
	context['formset']= formset
	return render(request, "tableview.html", context)

# blog/views.py
@login_required
def create_multiple_photos(request):
    name = request.user
    results = Master_db.objects.filter(name = name).order_by('-timesheetid')[:5]
    extra_forms = 1
   
    AddnewFormset = formset_factory(Masterdb, extra=extra_forms)
    formset = AddnewFormset()
    if request.method == 'POST':
        if 'additems' in request.POST and request.POST['additems']  == "true":
            
            formset_dictionary_copy = request.POST.copy()
            formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) + extra_forms
            print(formset_dictionary_copy)
            formset = AddnewFormset( formset_dictionary_copy)
        elif 'additems1' in request.POST and request.POST['additems1']  == "true":
            formset_dictionary_copy = request.POST.copy()
            formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) - extra_forms
            print(formset_dictionary_copy)
            formset = AddnewFormset( formset_dictionary_copy)
        
        else:
            formset = AddnewFormset(request.POST)
          
            if formset.is_valid():
                    for form in formset:
                        if form.cleaned_data:
                            entry = form.save(commit=False)
                            entry.save()
                            messages.success(request, 'Entries Saved Successfully')
                    return redirect('tableview')
    return render(request, 'table-view.html', {'formset': formset,'addEntry':results})

def userentry(request): 
       
            #results = Master_db.objects.all()
        time_threshold = datetime.now() - timedelta(days=14)
        now = timezone.now()
        name = request.user
        results = Master_db.objects.filter(date__gt = time_threshold, name = name).order_by("-timesheetid")
        # results = Master_db.objects.aggregate(
        #     last_14_days = models.Count('timesheetid',filter=models.Q(date=(now - timedelta(days=14)).date())),
        # )
        # status_filter = UserFilter(request.GET, queryset=results)
        return render(request, "userentry.html",{'userentry':results})

    
