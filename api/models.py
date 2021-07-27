from django.db import models
from django.contrib.auth.models import User


class Quota(models.Model):
    quota = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Resource(models.Model):
    resource = models.CharField(max_length=256)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
