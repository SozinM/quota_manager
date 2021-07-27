from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from api.serializers import UserSerializer, QuotaSerializer, ResourceSerializer
from api.models import Quota, Resource


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuotaViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    API endpoint that allows quotas to be viewed or edited.
    """
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer
    permission_classes = [permissions.IsAdminUser]


class ResourceViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Quota.objects.all()
    serializer_class = ResourceSerializer
