from django.urls import include, path
from django.contrib import admin
from rest_framework import routers
from CRM.views import UserWithRoleViewSet, ClientViewSet, EventViewSet, ContractViewSet,UserViewSet
from CRM.views import signup_view, login_view, CustomTokenObtainPairView, create_groups_view,custom_signup_view

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"users_with_roles", UserWithRoleViewSet, basename="users_with_roles")
router.register(r"clients", ClientViewSet, basename="clients")
router.register(r"events", EventViewSet, basename="events")
router.register(r"contracts", ContractViewSet, basename="contracts")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path('api-auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path("api-auth/signup/", custom_signup_view, name="signup"),
    path('make_groups/', create_groups_view, name='make_groups')
]
