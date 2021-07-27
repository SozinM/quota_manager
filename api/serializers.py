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

    def validate_quota(self, value):
        if value < -1:
            raise serializers.ValidationError("Incorrect quota value. "
                                              "Quota must be:\n"
                                              "-1 for restricted, 0 for unlimited or up to integer max for limited")


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['resource', 'user_id']
