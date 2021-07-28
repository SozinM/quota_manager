from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from api.serializers import UserSerializer, QuotaSerializer, ResourceSerializer
from api.models import Quota, Resource, QuotaUser


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [permissions.AllowAny]
    queryset = QuotaUser.objects.none()
    serializer_class = UserSerializer


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = QuotaUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class UserEditViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return QuotaUser.objects.filter(id=self.request.user.id)


class QuotaViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    API endpoint that allows quotas to be viewed or edited.
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ResourceSerializer

    def get_queryset(self):
        return Resource.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={**request.data, 'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ResourceAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()
