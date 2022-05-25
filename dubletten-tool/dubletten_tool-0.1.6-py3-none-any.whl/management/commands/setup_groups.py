from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import itertools as it
from collections import defaultdict, Counter
import json
from dubletten_tool.models import PersonProxy, Group, Suggestions, StatusButtonProxyType, StatusButtonGroupType, StatusButtonGroup, StatusButtonProxyType, StatusButtonProxy
from apis_core.apis_entities.models import Person
from apis_core.apis_metainfo.models import Collection

class Command(BaseCommand):

    def run_import_groups(self):
        #delete existing PersonProxy, Group and Button Objects
        PersonProxy.objects.all().delete()
        Group.objects.all().delete()
        StatusButtonGroupType.objects.all().delete()
        StatusButtonProxyType.objects.all().delete()
        StatusButtonGroup.objects.all().delete()
        StatusButtonProxy.objects.all().delete()
        
        ACC = Collection.objects.get(name="Import ACCESS full 13-10-21")
        SELECTION = Person.objects.exclude(collection__in=[ACC])
        
        df_per = pd.DataFrame(SELECTION.values("id","name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written")).set_index("id")
        per = df_per[["name", "first_name", "gender", "start_date", "end_date", "start_date_written", "end_date_written"]]
        #per["fullname"] = per.name + ", " + per.first_name
        per["sd"] = [str(d) for d in per["start_date"]]
        per["ed"] = [str(d) for d in per["end_date"]]

        self.stdout.write("Calculating Groups Started")
        for idx, (d, group) in enumerate(per.groupby(["name", "first_name", "gender", "sd", "ed"])):
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
                        g._gender = d[2]
                        g.save()

                    elif len(group) == 1:
                        s = group.index.to_list()[0]
                        per = Person.objects.get(id=s)
                        prox, c = PersonProxy.objects.get_or_create(person=per)
                        prox.status = "single"
                        prox.save()
        self.stdout.write("Finished: Calculating Groups")


    def create_ampel_buttons(self):
        self.stdout.write(f"Starting Create Ampel Buttons")
        types = [("Checked Members", "CM" ),("Checked Suggestions", "CSu" ),("Checked Singles", "CSi"),("Ready To Merge", "RM")]
        for el in types:
            btn, c = StatusButtonGroupType.objects.get_or_create(name=el[0], short=el[1])
            btn.add_to_all_groups()
            self.stdout.write(f"Added Button '{el[0]} to all Groups.")
        


    def calculate_names(self):
        self.stdout.write("Started: Calculate Names")
        
        for p in PersonProxy.objects.all():
            p._names = p.names_list
            p._first_names = p.first_names_list
            p.save()
        
        sn = {tuple(s.allnames) for s in PersonProxy.objects.all()}
        sn = [set(el) for el in sn]
        all_sn = {part for el in sn for part in el}
        
        sf = {tuple(s.allfirst_names) for s in PersonProxy.objects.all()}
        sf = [set(el) for el in sf]
        all_sf = {part for el in sf for part in el}


        p_n = defaultdict(list)
        p_f = defaultdict(list)
        [p_n[tuple(p.allnames)].append(p.id) for p in PersonProxy.objects.all()]    
        [p_f[tuple(p.allfirst_names)].append(p.id) for p in PersonProxy.objects.all()]    
        
        self.stdout.write("step 1 finished")
        
        def get_names(names_set, res_dic):
            self.stdout.write("running get names")
            res = defaultdict(list)
            for n in names_set:
                for k in res_dic:
                    if n in k:
                        res[n] += res_dic[k]
            return res
        
        res_n = get_names(all_sn, p_n)
        res_f = get_names(all_sf, p_f)
        
        self.stdout.write("step 2 finished, get names done")
        
        def get_per_dic(data):
            self.stdout.write("running get_per_dic")
            per_dic = defaultdict(set)
            for idx, i in enumerate(PersonProxy.objects.values_list("id")):
                test = i[0]
                for k, v in data.items():
                    if test in v:
                        per_dic[test] = per_dic[test].union(set(v))
                        per_dic[test].remove(test)
            return per_dic
        
        n = get_per_dic(res_n)
        f = get_per_dic(res_f)
        self.stdout.write("finished all calculations")
        
        full_res = defaultdict(set)

        for k,v in n.items():
        
            v2 = f[k]
            res = v.intersection(v2)
            if res:
                full_res[k] = res
            else:
                full_res[k] = set()
        
        data = {k:list(v) for k, v in full_res.items()}
        # with open("/Users/gregorpirgie/Desktop/full_res_new.json", "w") as file:
        #     data = json.dumps({k:list(v) for k, v in full_res.items()})
        #     file.write(data)
        self.stdout.write("Finished: Calculate Names")

        return data
        

  
    def handle(self, *args, **options):
        self.run_import_groups()
        self.create_ampel_buttons()
        data = self.calculate_names()
        #data = json.loads(data)
        Suggestions.objects.all().delete()
        Suggestions.objects.get_or_create(data=data)
        self.stdout.write("Finished: ALL PROCESSES")


