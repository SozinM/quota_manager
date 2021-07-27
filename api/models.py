from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Quota(models.Model):
    """
    Model that represents quota.
    values of the quota:
    -1 - admin prohibits users from creating any resources
    0 - user could create unlimited resources
    >1 - user could create limited resources
    """
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # 2^63-1 maximum integer in sqlite
    quota = models.IntegerField(default=0, validators=[MinValueValidator(-1), MaxValueValidator(pow(2, 63) - 1)])


class Resource(models.Model):
    resource = models.CharField(max_length=256, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
