from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.models import Quota, QuotaUser, Resource


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaUser
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = QuotaUser.objects.create_user(**validated_data)
        Quota.objects.create(id=user)
        return user


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ["id", "quota", "allowed"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["resource", "user_id"]

    def is_quota_suffice(self, data):
        quota_object = Quota.objects.filter(id=data["user_id"]).first()
        if not quota_object.allowed:
            raise serializers.ValidationError(
                _("User is prohibited from creating resources by Admin")
            )
        if quota_object.quota:
            if (
                Resource.objects.filter(user_id=data["user_id"]).count()
                >= quota_object.quota
            ):
                raise serializers.ValidationError(_("User's quota exceeded"))
        return data
