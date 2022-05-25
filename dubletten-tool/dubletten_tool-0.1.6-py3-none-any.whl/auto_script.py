from .models import Group, PersonProxy
from apis_core.apis_entities.models import Person
from apis_core.apis_metainfo.models import Collection
import pandas as pd

HSV = Collection.objects.get(name="Import HSV full 22-6-21")
HZAB = Collection.objects.get(name="Import HZAB full 10-3-21")
ACC = Collection.objects.get(name="Import ACCESS full 13-10-21")
MAN = Collection.objects.get(name="manually created entity")

persons = Person.objects.exclude(collection__in=[ACC])


df_per = pd.DataFrame(persons.values()).set_index("id")
per = df_per[["name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written"]]
per["fullname"] = per.name + ", " + per.first_name


singles = []
def get_groups():
    names_gender = []
    df_test = []
    frames = []
    c = 0
    for d, group in per.groupby(["fullname", "gender"]):
        if len(group) > 1:
            #log.info(f"{len(group)}, {d}, {[f for f in group.index]}")
            names_gender.append((len(group), d, group.index.to_list()))
            #df_test.append({"count":len(group), "key":d})
            c += len(group)
            #frames.append(group)
        elif len(group) == 1:
            singles.append(group.index.to_list()[0])
    
    return names_gender


ng = get_groups()



for s in singles:
    per = Person.objects.get(id=s)
    prox = PersonProxy.objects.get(person=per, status="single")
    prox.save()


