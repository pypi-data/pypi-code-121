from django.db import models
from apis_core.apis_entities.models import Person
from copy import deepcopy

# class Note(models.Model):
#     text = models.TextField(max_length=2000, null=True, blank=True)

class PersonProxy(models.Model):

    class Meta:
        ordering = ['person__name']
    # todo: __gpirgie__ rename to Deduplication Proxy or something like that
    status_choices = [
        ("candidate", "Candidate"),
        ("single", "Single"),
        ("merged", "Merged"),
    ]
    person = models.OneToOneField(Person, null=False, blank=False, on_delete=models.CASCADE)
    status = models.CharField(max_length=300, choices=status_choices, default="single")
    marked = models.BooleanField(default=False)
    note = models.TextField(max_length=2000, null=True, blank=True)

    _names = models.JSONField(null=True)
    _first_names = models.JSONField(null=True)


    @property
    def alt_names(self):
        nach = ["alternative name", "alternativer Nachname", "Nachname verheiratet", "Nachname alternativ verheiratet", "Nachname alternativ vergeiratet"]
        return [l[0].strip() for l in self.person.label_set.filter(label_type__name__in=nach).values_list("label")]

    @property
    def name_verheiratet(self):
        ver = ["Nachname verheiratet", "Nachname alternativ verheiratet", "Nachname alternativ vergeiratet"]
        return [l[0].strip() for l in self.person.label_set.filter(label_type__name__in=ver).values_list("label")]

    @property 
    def alt_first_names(self):
        return [l[0].strip() for l in self.person.label_set.filter(label_type__name="alternativer Vorname").values_list("label")]

    @property
    def names_list(self):
        name = self.person.name
        alt_names = self.alt_names
        alt_names.append(name)
        return alt_names

    @property
    def first_names_list(self):
        first_name = self.person.first_name
        alt_first_names = self.alt_first_names
        alt_first_names.append(first_name)
        return alt_first_names

    @property
    def names_set(self):
        return set(self.names_list)

    @property
    def first_names_set(self):
        return set(self.first_names_list)

    @property
    def allnames(self):
        return set(self._names)

    @property
    def allfirst_names(self):
        return set(self._first_names)

    @property
    def name(self):
        return f"{self.person.name}, {self.person.first_name}"



class Group(models.Model):
    """Group: A collection of Person-Instances storing possible duplicates. 
    Each group should run through several filter, split and add processes to finally be merged into one entity. 
    A Group holds GroupingCandidates, which serve as proxies for the actual Person-instances.

    Args:
        models (_type_): 
        
    Fields:
    """

    class Meta:
        ordering = ["name"]

    status_choices_group = [
        ("unchecked", "unchecked"),
        ("checked group", "checked group"),
        ("checked for other groups", "checked for other groups"),
        ("checked all members", "checked all members"),
        ("ready to merge", "ready to merge"),
        ("merged", "merged")
    ]
    name = models.CharField(max_length=600, blank=True)
    members = models.ManyToManyField(PersonProxy, blank=True)
    status = models.CharField(max_length=300, choices=status_choices_group, default="unchecked")
    _gender = models.CharField(max_length=255, null=True, blank=True)
    marked = models.BooleanField(default=False)
    note = models.TextField(max_length=2000, null=True, blank=True)

    @property
    def all_notes(self):
        notes = [{"person_id":el.person.id, "note":el.note} for el in self.members.all()]
        return notes

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        self._gender = value

    @property
    def buttons(self):
        return self.statusbuttongroup_set.all()

    @property
    def count(self):
        return self.members.all().count()

    @property
    def all_names(self):
        names = set()
        for m in self.members.all():
            names = names.union(m.names)
        
        return names

    @property
    def all_first_names(self):
        first_names = set()
        for m in self.members.all():
            first_names = first_names.union(m.first_names)
        
        return first_names


    def check_status(self, status_dict):
        flag = True
        for k, v in status_dict.items():
            if v == "true":
                val = True
            else: 
                val = False

            if StatusButtonGroup.objects.filter(kind__id=k, value=val, related_instance=self):
                continue
            else:
                flag = False
        
        return flag



class Suggestions(models.Model):
    data = models.JSONField(null=True, blank=True)


class StatusButtonGroupType(models.Model):
    name = models.CharField(max_length=600, null=False, blank=False)
    short = models.CharField(max_length=4, null=False, blank=False, default="BT")

    def add_to_all_groups(self):
        all_groups = Group.objects.all()
        for g in all_groups:
            sb, c = StatusButtonGroup.objects.get_or_create(kind=self, related_instance=g)
            sb.save()

class StatusButtonGroup(models.Model):
    kind = models.ForeignKey(StatusButtonGroupType, on_delete=models.CASCADE)
    related_instance = models.ForeignKey(Group, on_delete=models.CASCADE)
    value = models.BooleanField(default=False)

    def toggle_status(self):
        self.value = not self.value
        self.save()

class StatusButtonProxyType(models.Model):
    name = models.CharField(max_length=600, null=False, blank=False)

    def add_to_all_groups(self):
        all_proxies = PersonProxy.objects.all()
        for p in all_proxies:
            sb, c = StatusButtonProxy.objects.get_or_create(kind=self, related_instance=p)
            sb.save()

class StatusButtonProxy(models.Model):
    kind = models.ForeignKey(StatusButtonProxyType, on_delete=models.CASCADE)
    related_instance = models.ForeignKey(PersonProxy, on_delete=models.CASCADE) 
    value = models.BooleanField(default=False)







#     removed = models.ManyToManyField(GroupingCandidate, blank=True, null=True)
#     added = models.ManyToManyField(GroupingCandidate, blank=True, null=True)




    




