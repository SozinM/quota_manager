from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers
from rest_framework_simplejwt import views as jwt_views

from api import views


schema_view = get_schema_view(
    openapi.Info(
        title="Quota Manager",
        default_version="v1",
        description="Quota Manager",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="mikawamp@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register(r"register", views.UserCreateViewSet)
router.register(r"users", views.RetrieveDeleteUserViewSet, basename="^users/$")
router.register(r"resources", views.UserResourceViewSet, basename="resource/$")
router.register(r"admin/users", views.AdminUserViewSet)
router.register(r"admin/quotas", views.AdminQuotaViewSet)
router.register(r"admin/resources", views.AdminResourceViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("login/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
