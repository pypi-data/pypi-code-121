import Levenshtein as lev
from .models import PersonProxy, Group, Suggestions

singles = PersonProxy.objects.filter(status="single")

def get_levensthein(person, distance=2):
    print("levensthein running")
    name = person.name
    first = person.first_name
    persons = [(p.person.name, p.person.first_name, p.person.id, p) for p in singles]
    res = []
    for n, f, pk, p in persons:
        dist_n = lev.distance(name, n)
        dist_f = lev.distance(first, f)

        if dist_n == 0:
            if 0 < dist_f <= distance:
                #res.append((n,f, pk))
                res.append(p)


        elif dist_f == 0:
            if 0 < dist_n <= distance:
                #res.append((n,f, pk))
                res.append(p)

    return res


def check_all_names(obj):
    """
    Get Levensthein distance for obj against all other groups and singles. 
    Obj: Group or a PersonProxy instance.
    """
    print("all names running")
    if isinstance(obj, Group):
        names = obj.all_names
        first_names = obj.all_first_names
    
    elif isinstance(obj, PersonProxy):
        names = obj.names
        first_names = obj.first_names

    res_g = []
    res_s = []

    for s in singles:
        if s.first_names_set.intersection(first_names) and s.names_set.intersection(names):
            res_s.append(s)
    
    # for g in Group.objects.all():
    #     if g.all_names.intersection(names) and g.all_first_names.intersection(first_names):
    #         res_g.append(g)
    
    return res_g, res_s

def get_name_suggestions(pp_pk):
    print("get_name_suggestions running")
    suggestions = Suggestions.objects.all()[0].data

    return suggestions.get(str(pp_pk), [])






    


