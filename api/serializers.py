from django.contrib.auth.models import User
from api.models import Quota, Resource
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        Quota.objects.create(id=user)
        return user


class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'quota']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['resource', 'user_id']
