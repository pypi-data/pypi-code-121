from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from django.utils.decorators import method_decorator
# Create your views here.
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
#from .grouping_script_1 import run
from .models import Group, PersonProxy, StatusButtonGroup, StatusButtonProxy, StatusButtonGroupType
import json
from .suggestions import get_levensthein, check_all_names, get_name_suggestions
#run()
from .forms import GroupForm, PersonProxyForm


def create_new_buttons(group):
         
    for btn in StatusButtonGroupType.objects.all():
        b, c = StatusButtonGroup.objects.get_or_create(kind=btn, related_instance=group)
        b.save()

    group.save()

@method_decorator(login_required, name="dispatch")
class getToolPage(TemplateView):
    template_name = "tool_page.html"
    print("getToolPage called")

    def get_context_data(self, **kwargs):
        #ng = get_groups()
        groups = Group.objects.all()
        #singles = PersonProxy.objects.filter(status="single")
        context = {}

        context["groups"] = groups
        context["Buttons"] = StatusButtonGroupType.objects.all()
        #context["singles"] = singles
        return context

def calculate_person_suggestions(per_id=None, pp_id=False):
    if not pp_id:
        pp = PersonProxy.objects.get(person__id=per_id)
    else:
        pp = PersonProxy.objects.get(id=pp_id)
    if pp.status == "candidate":
        pgroup = pp.group_set.all()[0]
    else:
        pgroup = None
    #template = "person_suggestions.html"
    lev_data = get_levensthein(pp.person)
    l_singles = []
    l_groups = []
    for el in lev_data:
        if el.status == "single":
            l_singles.append(el)
        elif el.status == "candidate":
            group = el.group_set.all()[0]
            l_groups.append(group)
        else:
            continue
    levs = {"groups": list(set(l_groups)), "singles": list(set(l_singles))}

    #all_names = check_all_names(pp)
    names = get_name_suggestions(pp.id)
    all_names = PersonProxy.objects.filter(id__in=names)
    names_singles = all_names.filter(status="single")
    print(names_singles)
    in_group = all_names.filter(status="candidate")
    names_groups = {g for p in in_group for g in p.group_set.all()} 
    if pgroup:
        names_groups.discard(pgroup)    

    data = {"pp": pp, "levs":levs, "names_groups":names_groups, "names_singles":names_singles}

    return data


def get_person_suggestions(request, **kwargs):

    if request.method == "GET":
        per_id = kwargs.get("per_id")
        print("per id was", per_id)
        template = "person_suggestions.html"
        
        data = calculate_person_suggestions(per_id=per_id)

        pp = data["pp"]
        levs = data["levs"]
        names_groups = data["names_groups"]
        names_singles = data["names_singles"]
        # pp = PersonProxy.objects.get(person__id=per_id)
        # if pp.status == "candidate":
        #     pgroup = pp.group_set.all()[0]
        # else:
        #     pgroup = None
        # template = "person_suggestions.html"
        # lev_data = get_levensthein(pp.person)
        # l_singles = []
        # l_groups = []
        # for el in lev_data:
        #     if el.status == "single":
        #         l_singles.append(el)
        #     elif el.status == "candidate":
        #         group = el.group_set.all()[0]
        #         l_groups.append(group)
        #     else:
        #         continue
        # levs = {"groups": list(set(l_groups)), "singles": list(set(l_singles))}

        # #all_names = check_all_names(pp)
        # names = get_name_suggestions(pp.id)
        # all_names = PersonProxy.objects.filter(id__in=names)
        # names_singles = all_names.filter(status="single")
        # print(names_singles)
        # in_group = all_names.filter(status="candidate")
        # names_groups = {g for p in in_group for g in p.group_set.all()} 
        # if pgroup:
        #     names_groups.discard(pgroup)          
        context = {
            "instance": pp,
            "levs": levs,
            "names": {"groups": list(names_groups), "singles":names_singles}
        }
        html = render_to_string(template, context, request)

        return JsonResponse({"html":html})

def get_group_suggestions(request, **kwargs):

    if request.method == "GET":
        g_id = kwargs.get("group_id")
        group = Group.objects.get(id=g_id)
        members = group.members.all()
        print(members)
        names_groups = set()
        names_singles = set()
        levs = {"groups":set(), "singles":set()}

        for m in members:
            data = calculate_person_suggestions(pp_id=m.id)
            names_groups = names_groups.union(set(data["names_groups"]))
            names_singles = names_singles.union(set(data["names_singles"]))
            levs["groups"] = levs["groups"].union(set(data["levs"]["groups"]))
            levs["singles"] = levs["singles"].union(set(data["levs"]["singles"]))


        template = "person_suggestions.html"
        context = {
            "instance": group,
            "levs": levs,
            "names": {"groups": list(names_groups), "singles":names_singles}
        }

        html = render_to_string(template, context, request)

        return JsonResponse({"html":html})
    """
    TODO: Implement this for groups. 
    Ignore Levensthein, but accumulate all names suggestions 
    for all group members, ignoring the calling group.
    """

def rename_group(request):
    if request.method == "POST":
        print(request.POST)
        data = json.loads(request.POST.get("data"))
        new_name = data.get("new_name")
        if not new_name or new_name in [None, "Null", "none", "None", "null"]:
            new_name = "Unnamed Group"
        g_id = data.get("g_id")
        group = Group.objects.get(id=g_id)
        old_name = Group.name
        group.name = new_name 
        group.save()
        msg = f"Renamed Group {g_id} from {old_name} to {new_name}."

        return JsonResponse({"data":{"group_id": g_id, "msg":msg, "count":group.count, "new_name":group.name}})

class HandleNoteForm(View):

    # todo: rename everything related in here from group to note (noteForm, inst_id instead of g-id, etc)

    def get(self, *args, **kwargs):
        template = "note_form.html"
       
        g_id = self.kwargs.get("g_id")
        type = self.kwargs.get("type")
        print("get method of handlegroupfrom called, id and type is: ", g_id, type)


        if type == "group":
            instance = Group.objects.get(id=g_id)
            form = GroupForm(g_id, instance=instance)

        else: 
            instance = PersonProxy.objects.get(person__id=g_id)
            form = PersonProxyForm(g_id, instance=instance)

        html = render_to_string(template, {"form":form, "instance":instance}, self.request)

        return JsonResponse({"html": html, "success":True})

    def post(self, *args, **kwargs):
        g_id = self.kwargs.get("g_id")
        type = self.kwargs.get("type")
        print("post method of handlegroupfrom called, id and type is: ", g_id, type)


        if type == "group":
            instance = Group.objects.get(id=g_id)
            form = GroupForm(g_id, self.request.POST, instance=instance)

        else:
            instance = PersonProxy.objects.get(person__id=g_id)
            form = PersonProxyForm(g_id, self.request.POST, instance=instance)
            

        success = False
        if form.is_valid():
            ent = form.save()
            ent.save()

            print("SAVED NOTE")

            success = True
            res_msg = "Saved Note!"
        else:
            res_msg = "Form was invalid"

        return JsonResponse({"msg": res_msg, "success":success, "inst_id":g_id, "type":type})

def get_all_notes(request):
    template = "all_notes.html"
    singles = [{"name":s.name, "id":s.person.id, "note":s.note} for s in PersonProxy.objects.filter(status="single") if s.note]
    candidates = [s.group_set.all()[0] for s in PersonProxy.objects.filter(status="candidate") if s.note]
    groups = [g for g in Group.objects.all() if g.note] + candidates

    groups = set(groups)

    groups = [{"name": g.name, "id":g.id, "note":g.note} for g in groups]
    context = {"groups": groups, "members":candidates, "singles":singles}

    html = render_to_string(template, context, request) 

    return JsonResponse({"html":html})



def get_groups(request, **kwargs):

    if request.method == "GET":
        filter = kwargs.get("val")
        filter = filter.replace("__", " ")
        if filter == "get_all_groups":
            filter = None
        print("filter set to: ", filter)

        d = json.loads(request.GET.get("data"))
        print(d, type(d))
        gender = kwargs.get("gender")
        print("gender arrived as: ", gender)
        if gender == "Other":
            gender = [None, "third gender"]
        else: 
            gender = [gender.lower()]
            
        print(gender)
        context = {}
        if not filter:
            groups = Group.objects.filter(_gender__in=gender)

        else: 
            groups = Group.objects.filter(name__istartswith=filter, _gender__in=gender)

        groups = list(groups)
       
        #print(groups)
        
      

        if len(groups) > 100:
            test_groups = set(groups)
            for k, v in d.items():
                if v == "true":
                    val = True
                else: 
                    val = False
                temp = [b.related_instance for b in StatusButtonGroup.objects.filter(kind__id=int(k), value=val)]
                test_groups = test_groups.intersection(set(temp))
            res = [g for g in groups if g in test_groups]
        else:
            res = [g for g in groups if g.check_status(d)]
            res = list(res)

        context["groups"] = res           
        count = len(context["groups"])
        context["group_count"] = count

        html = render_to_string("group_list.html", context, request)

        return JsonResponse({"html": html, "group_count": count})


def renderNoteHtml(instance, type, request):
    template = "note_template.html"

    if instance.note:
        note = instance.note
    else: 
        note = ""

    if type == "group":
        name = instance.name
    else: 
        name = f"{instance.person.name}, {instance.person.first_name}"
        instance = instance.person

    context = {"instance": instance, "note":note, "name":name, "type":type}

    html = render_to_string(template, context, request)

    return html



def getNoteJSON(request, **kwargs):

    if request.method == "GET":
        pk = kwargs.get("inst_id")
        type = kwargs.get("type")
        print("in getNoteJson, pk, type is: ", pk, type)
        if type == "group":
            instance = Group.objects.get(id=pk)
        else: 
            instance = PersonProxy.objects.get(person__id=pk)
        
        html = renderNoteHtml(instance, type, request)

        return JsonResponse({"html":html, "success":True})

def get_singles(request, **kwargs):
    
    if request.method == "GET":
        #singles = {s.id: {"name":s.person.name, "first_name": s.person.first_name,"start": s.person.start_date,"end":s.person.end_date} for s in PersonProxy.objects.filter(status="single")}
        
        # text = kwargs.get("val")
        # type = kwargs.get("type")
        # print("text arrived as: ", text)
        
        # if not text:
        #     singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(status="single")]
        # else:
        #     print("used filtered singles")
            
        #     text = text.replace("__", " ")

        #     if type == "name":
        #         singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(person__name__istartswith=text).filter(status="single")]
        #     elif type == "first_name":
        #         singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(person__first_name__istartswith=text).filter(status="single")]

        #     print("filtered singles len: ", len(singles))

        text_name = kwargs.get("val_name")
        text_first = kwargs.get("val_first")
        print(f"Arrived as - name: {text_name}, first: {text_first}")

        gender = kwargs.get("gender")
        print("gender arrived as: ", gender)
        if gender == "Other":
            gender = [None, "third gender"]
        else: 
            gender = [gender.lower()]

        if text_name == "false":
            text_name = False
        else: 
            text_name = text_name.replace("__", " ")

        if text_first == "false":
            text_first = False
        else:
            text_first = text_first.replace("__", " ")

        if not text_name and not text_first:
            singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(status="single", person__gender__in=gender)]
        elif not text_first:
            singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(person__name__istartswith=text_name).filter(status="single", person__gender__in=gender)]
        elif not text_name:
            singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(person__first_name__icontains=text_first).filter(status="single", person__gender__in=gender)]
        else:
            singles = [(s.person.id, s.person.name, s.person.first_name, s.person.start_date, s.person.end_date) for s in PersonProxy.objects.filter(person__first_name__icontains=text_first, person__name__istartswith=text_name).filter(status="single", person__gender__in=gender)]

        return JsonResponse({"singles":singles})

def get_group_ajax(request, **kwargs):

    if request.method == "GET":
        g_id = kwargs.get("g_id")
        group = Group.objects.get(id=g_id)
        members = [(v, [r for r in v.person.personinstitution_set.all().order_by("relation_type__name")]) for v in group.members.all()]
        members.sort(key=lambda x: len(x[1]), reverse=False)
        context = {
            "group":group,
            "members": members,
        }

        html = render_to_string("member_list.html", context, request)

        return JsonResponse({"html":html})
        
def get_single_ajax(request, **kwargs):

    if request.method == "GET":
        s_id = kwargs.get("s_id")
        single = PersonProxy.objects.get(person__id=s_id)
        if not single.status == "single":
            print("WAS NOT A SINGLE")
        
        context = {
            "p": single,
            "rels": [r for r in single.person.personinstitution_set.all().order_by("relation_type__name")]
        }

        html = render_to_string("singles_list.html", context, request)
        return JsonResponse({"html":html})

def update_group_checkboxes(request, **kwargs):
    if request.method == "POST":
        template = "group_buttons.html"
        btn_id = kwargs.get("btn_id")
        g_id = kwargs.get("group_id")

        print(btn_id)
        print(g_id)
        group = Group.objects.get(id=g_id)
        btn = StatusButtonGroup.objects.get(id=btn_id)
        btn.toggle_status()
        html = render_to_string(template, {"group":group}, request)
        return JsonResponse({"html":html})


def create_new_group(request):
    if request.method == "POST":
        d = json.loads(request.POST.get("DATA"))


        data = d.get("data")
        name = d.get("new_name")
    
        if not name:
            name = "New Group"

        new_group = Group.objects.create(name=name)
        if name == "New Group":
            new_group.name += " "+str(new_group.id)
            new_group.save()

        updates = {}
        former_singles = []
        for k, v in data.items():
            print(k, v)
            if v:
                if k != "singles":
                    group = Group.objects.get(id=k)
                   
                pers = PersonProxy.objects.filter(person__id__in=v)
                print("pers is", pers)
                for p in pers:
                    if k != "singles":
                        group.members.remove(p)
                        group.save()
                    else: 
                        p.status = "candidate"
                        former_singles.append(p.person.id)
                        p.save()
                    new_group.members.add(p)

                if k != "singles":
                    count = group.count
                    g_id = group.id
                    if count == 0:
                        print("In count == 0 gid, count", g_id, count)
                        group.delete()
                        

                    elif count == 1:
                        print("IN coutn == 1 gid, count", g_id, count)

                        per = group.members.all()[0]
                        per.status = "single"
                        per.save()
                        group.delete()
                        count = 0


                    else:
                        group.save()
               
                    updates.update({g_id:count})
                new_group._gender = new_group.members.all()[0].person.gender
                new_group.save()
        create_new_buttons(new_group)

        print("updates is: ", updates)
        res = {"new_group_id": new_group.id, "new_group": new_group.name, "new_group_count":new_group.count, "former_singles":former_singles,"group_updates":updates}
        
        #todo: add message 
        return JsonResponse({"data":res})




def merge_groups(request):
    if request.method == "POST":
        d = json.loads(request.POST.get("DATA"))
        print(d)
        name = d.get("new_name")
        groups = d.get("groups")
        singles = d.get("singles")

        new_group = Group.objects.create(name=name)
        if groups:
            for g in groups:
                group = Group.objects.get(id=g)
                for m in group.members.all():
                    new_group.members.add(m)
                note = group.note
                if note and new_group.note:
                    new_group.note += f"\n[[ Notes from merged group ({g}):{note}]]"
                elif note:
                    new_group.note = f"[[ Notes from merged group ({g}):{note}]]"

                new_group.save()
                group.delete()

        if singles: 
            for s in singles:
                print("singles was true")
                print("single id was: ", s)
                pp = PersonProxy.objects.get(person__id=s)
                pp.status = "candidate"
                pp.save()
                new_group.members.add(pp)
            new_group.save()
        
        new_group._gender = new_group.members.all()[0].person.gender
        new_group.save()
        create_new_buttons(new_group)
        
        
        # todo : add message 
        return JsonResponse({"remove_groups": groups, "remove_singles":singles, "add": [new_group.id, new_group.name, new_group.count]})
            



def remove_member(request, **kwargs):
    if request.method == "GET":
        group_id = kwargs.get("group_id")
        per_id = kwargs.get("per_id")

        group = Group.objects.get(id=group_id)
        per = PersonProxy.objects.get(person__id=per_id)
        group.members.remove(per)
        per.status = "single"
        group.save()
        per.save()
        updates = {}

        count = group.count
        if count == 0:
            group.delete()
            

        elif count == 1:
            per = group.members.all()[0]
            per.status = "single"
            per.save()
            group.delete()
            count = 0

        else:
            group.save()
        
        updates.update({group_id:count})

        #todo: add message
        return JsonResponse({"data":updates})

            


