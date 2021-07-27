from django.db import models
from django.contrib.auth.models import User


class Quota(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quota = models.IntegerField(default=0)


class Resource(models.Model):
    resource = models.CharField(max_length=256, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
