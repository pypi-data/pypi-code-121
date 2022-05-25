import os
import pandas as pd
from copy import deepcopy
from collections import Counter, defaultdict
import numpy as np 
import re
from apis_core.apis_entities.models import Person, Institution, Place, Event, Work
from apis_core.apis_relations.models import *
from apis_core.apis_metainfo.models import Collection
from apis_core.apis_vocabularies.models import *
from .models import PersonProxy, Group
#import Levenshtein as lev
import logging


log = logging.getLogger("mylogger")
log.setLevel(logging.INFO)

log.info("logger init")

# # base entities
# P = Person
# I = Institution
# PL = Place
# W = Work
# E = Event

# #functions
# F = PersonInstitutionRelation

# #other relations
# PI = PersonInstitution
# PE = PersonEvent
# PP = PersonPlace
# IP = InstitutionPlace

# #collections
# HSV = Collection.objects.get(name="Import HSV full 22-6-21")
# HZAB = Collection.objects.get(name="Import HZAB full 10-3-21")
# ACC = Collection.objects.get(name="Import ACCESS full 13-10-21")
# MAN = Collection.objects.get(name="manually created entity")

# #other
# ENTS = [P, I, PL, W, E]

# def get_hs(instname):
#     if "(" in instname:
#         temp = instname.replace("(", "$", 1)
#         hs = temp.split("$")[1][:-1]
#         return hs
#     else:
#         return None


df_per = pd.DataFrame(Person.objects.values("id","name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written")).set_index("id")
per = df_per[["name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written"]]
#per["fullname"] = per.name + ", " + per.first_name
per["sd"] = [str(d) for d in per["start_date"]]
per["ed"] = [str(d) for d in per["end_date"]]


for d, group in per.groupby(["name", "first_name", "gender", "sd", "ed"]):
            bd, dd = d[3], d[4]
            bd = bd.replace("None", "")
            dd = dd.replace("None", "")
            if len(group) > 1:
                if bd and dd:
                    name = (f"{d[0]}, {d[1]} [B+D]")
                elif bd:
                    name = (f"{d[0]}, {d[1]} [B]")
                elif dd:
                    name = (f"{d[0]}, {d[1]} [D]")
                else:
                    name = (f"{d[0]}, {d[1]}")

                g, c = Group.objects.get_or_create(name=name)
                index = group.index.to_list()
                for ix in index:
                    gm, c = PersonProxy.objects.get_or_create(person=Person.objects.get(id=ix))
                    gm.status="candidate"
                    gm.save()
                    g.members.add(gm)
                
            elif len(group) == 1:
                s = group.index.to_list()[0]
                per = Person.objects.get(id=s)
                prox, c = PersonProxy.objects.get_or_create(person=per)
                prox.status = "single"
                prox.save()



# for d, group in per.groupby(["name", "first_name", "gender", "sd", "ed"]):
#     bd, dd = d[3], d[4]
#     bd = bd.replace("None", "")
#     dd = dd.replace("None", "")


# def run():
#     df_per = pd.DataFrame(Person.objects.all().values()).set_index("id")
#     per = df_per[["name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written"]]
#     #per["fullname"] = per.name + ", " + per.first_name
#     singles = []
#     def get_groups():
#         names_gender = []
#         df_test = []
#         frames = []
#         c = 0
#         for d, group in per.groupby(["name", "first_name", "gender"]):
#             if len(group) > 1:
#                 #log.info(f"{len(group)}, {d}, {[f for f in group.index]}")
#                 names_gender.append((len(group), d, group.index.to_list()))
#                 #df_test.append({"count":len(group), "key":d})
#                 c += len(group)
#                 #frames.append(group)
#             elif len(group) == 1:
#                 singles.append(group.index.to_list()[0])
#         return names_gender


#     ng = get_groups()


#     def create_groups():   
#         for count, el in enumerate(ng):
#             group, c = Group.objects.get_or_create(name=f"{el[1][0]} [{el[1][1]}]")
#             print(f"{count}/{len(ng)}")
#             for index in el[2]:
#                 gm, c = PersonProxy.objects.get_or_create(person=Person.objects.get(id=index))
#                 group.members.add(gm)
#                 gm.status="candidate"

#     create_groups()

#     for s in singles:
#         per = Person.objects.get(id=s)
#         prox = PersonProxy.objects.create(person=per, status="single")
#         prox.save()

#run()

###### Levenshtein Distance #####

# DISTANCE_VALUE = 2
# def lev_distance(a, series, container):
#     for pk, b in series.items():
#         dist = lev.distance(a,b)
#         if 0 < dist <= DISTANCE_VALUE:
#             container.append((dist, b, pk))
#     return container

# test = "Müller"
# container = []

# #container = lev_distance(test, per.name, container)




