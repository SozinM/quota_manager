from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework_simplejwt import views as jwt_views


router = routers.DefaultRouter()
router.register(r'users', views.UserCreateViewSet)
router.register(r'admin/users', views.UserAdminViewSet)
router.register(r'users/<int:pk>', views.UserEditViewSet, basename="^users/{pk}/$")
router.register(r'admin/quotas', views.QuotaViewSet)
router.register(r'resources', views.ResourceViewSet, basename="^resource/$")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
