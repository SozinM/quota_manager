from django.contrib.auth.models import User
from api.models import Quota, Resource, QuotaUser
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
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

