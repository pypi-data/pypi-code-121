from django.db import models


class Alphabet(models.Model):

    display_name = models.CharField(max_length=25, null=True)

    name = models.CharField(max_length=25, null=True)


class TestModel(models.Model):

    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    f3 = models.CharField(max_length=10, null=True, blank=False)
    f4 = models.CharField(max_length=10, null=True, blank=False)
    f5 = models.CharField(max_length=10)
    f5_other = models.CharField(max_length=10, null=True)
    alphabet = models.ManyToManyField(Alphabet)
