from __future__ import unicode_literals
from django.db import models


class ApiUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=100)
    expires_timestamp = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.username


class BirthDayEmails(models.Model):
    date = models.DateField(unique=True)
    birth_days_emailed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.date
