from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class QuotaUser(AbstractUser):
    """
    Model for email auth based on AbstractUser
    """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Quota(models.Model):
    """
    Model that represents quota.
    values of the quota:
    0 - user could create unlimited resources
    >1 - user could create limited resources
    allowed: True - user could create resources, False - user can't create resources
    """
    id = models.OneToOneField(QuotaUser, on_delete=models.CASCADE, primary_key=True)
    # 2^63-1 maximum integer in sqlite
    quota = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(pow(2, 63) - 1)])
    allowed = models.BooleanField(default=True)


class Resource(models.Model):
    """
    Model that represents resource linked to user
    """
    resource = models.CharField(max_length=256, unique=True)
    user_id = models.ForeignKey(QuotaUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.resource
