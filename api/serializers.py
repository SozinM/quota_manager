from django.utils.translation import gettext_lazy as _
from api.models import Quota, Resource, QuotaUser
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaUser
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = QuotaUser.objects.create_user(**validated_data)
        Quota.objects.create(id=user)
        return user


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'quota', 'allowed']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['resource', 'user_id']

    def validate(self, data):
        quota_object = Quota.objects.filter(id=data['user_id']).first()
        print(quota_object.allowed, quota_object.quota)
        if not quota_object.allowed:
            raise serializers.ValidationError(_("User is prohibited from creating resources by Admin"))
        if quota_object.quota:
            print(data)
            if Resource.objects.filter(user_id=data['user_id']).count() >= quota_object.quota:
                raise serializers.ValidationError(_("User's quota exceeded"))
        return data

