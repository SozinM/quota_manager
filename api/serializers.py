from django.contrib.auth.models import User, Group
from api.models import Quota, Resource
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class QuotaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Quota
        fields = ['quota', 'user_id']


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Resource
        fields = ['resource']
