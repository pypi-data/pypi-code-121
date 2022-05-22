import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone

# Create your models here.

class Question(models.Model):
  question_text = models.CharField(max_length=200)
  pub_date = models.DateTimeField('date published')
  
  def __str__(self) -> str:
      return self.question_text
  
  # def was_published_recently(self):
  #   return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
  
  # The following is a decorator for the 'was_published_recently' method
  # See https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
  @admin.display(
    boolean=True,
    ordering='pub_date',
    description='Published recently?',
  )
  def was_published_recently(self):
    now = timezone.now()
    return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  choice_text = models.CharField(max_length=200)
  votes = models.IntegerField(default=0)

  def __str__(self) -> str:
      return self.choice_text
