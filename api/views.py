from django.db import transaction
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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # add id from token to data for resource creation
        serializer = self.get_serializer(data={**request.data, 'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        # check that user have sufficient quota to create resource
        serializer.is_quota_suffice(serializer.validated_data)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        # add id from token to data for resource creation
        serializer = self.get_serializer(instance, data={**request.data, 'user_id': request.user.id}, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ResourceAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()
