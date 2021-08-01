from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from api.serializers import UserSerializer, QuotaSerializer, ResourceSerializer
from api.models import Quota, Resource, QuotaUser
from drf_yasg.utils import swagger_auto_schema


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="API endpoint that provides registration of the user", responses={400: "User already exist"}
))
class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that provides registration of the user
    """
    permission_classes = [permissions.AllowAny]
    queryset = QuotaUser.objects.none()
    serializer_class = UserSerializer


class AdminUserViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    API endpoint that allows administrator to create, delete and list users
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = QuotaUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class RetrieveDeleteUserViewSet(mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """
    API endpoint that allows users to view data of himself or delete himself.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return QuotaUser.objects.filter(id=self.request.user.id)


class AdminQuotaViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows admin to edit, list and retrieve user's quota
    """
    permission_classes = [permissions.IsAdminUser]
    queryset = Quota.objects.all()
    serializer_class = QuotaSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="API endpoint that provides registration of the user",
    responses={400: "User is prohibited from creating resources by Admin\n"
                    "User's quota exceeded"}
))
class UserResourceViewSet(viewsets.ModelViewSet):
    """
    Endpoint that allows user to CRUD and list resources of this user
    On create this endpoint check that user's quota is sufficient and user allowed to create resources
    """
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


class AdminResourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows admin to CRUD and list resources of all users
    On create this endpoint ignores quota
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()
