from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class QuotaUser(AbstractUser):
    """
    Model for email auth based on AbstractUser
    """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


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

    def clean(self):
        quota_object = Quota.objects.filter(id=self.user_id)
        if not quota_object.allowed:
            raise ValidationError(_("User is prohibited from creating resources by Admin"))
        if quota_object.quota:
            if Resource.objects.filter(user_id=self.user_id).count() >= quota_object.quota:
                raise ValidationError(_("User's quota exceeded"))

