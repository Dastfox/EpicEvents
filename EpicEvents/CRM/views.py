import json
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

from .models import Contract, Client, UserWithRole, Event
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.db.models.signals import m2m_changed
from .permissions import ContractPermissions, ClientPermissions, EventPermissions
from .serializers import (
    ContractSerializer,
    ClientSerializer,
    UserSerializer,
    UserWithRoleSerializer,
    EventSerializer,
)

from rest_framework_simplejwt.views import TokenRefreshView

@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(sender, instance, action, *args, **kwargs):
    print(UserWithRole.Role.choices)
    if action == "post_add":
        # Handle addition to a group
        for group in instance.groups.all():
            group_name = group.name
            try:
                print(group_name)
                role_value = next(val for val, name in UserWithRole.Role.choices if name == group_name)
                user_with_role, created = UserWithRole.objects.get_or_create(user=instance, role=role_value)
                user_with_role.role = role_value
                user_with_role.save()
            except StopIteration:
                print(f"No role found for group: {group_name}")

    elif action == "post_remove":
        # Handle removal from a group
        for group in kwargs.get('pk_set', []):
            group_obj = Group.objects.get(pk=group)
            group_name = group_obj.name
            try:
                role_value = next(val for val, name in UserWithRole.Role.choices if name == group_name)
                user_with_role = UserWithRole.objects.filter(user=instance, role=role_value)
                if user_with_role.exists():
                    user_with_role.delete()
            except StopIteration:
                print(f"No role found for group: {group_name}")



def create_groups_view(request):
    roles = ["Sales","Management","Support"]  # Get the list of roles
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)
            
    for user_with_role in UserWithRole.objects.all():
        role_name = user_with_role.get_role_display()  # Returns the string representation of the role
        group = Group.objects.get(name=role_name)  # Get the Group object
        user_with_role.user.groups.add(group)  # Add the User object to the group

    return JsonResponse({"status": "success", "message": "Groups created and users assigned successfully."})

class CustomTokenRefreshView(TokenRefreshView):
    """
    View to return a new access token given a valid refresh token
    """
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse(serializer.validated_data, status=200)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View to return a new access token given a valid refresh token
    """
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return JsonResponse(serializer.validated_data, status=200)
    


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Create a new token 
            refresh = RefreshToken.for_user(user)
            # return django admin panel
            return redirect(reverse("admin:index"))
        else:
            error = "Invalid username or password."

    else:
        error = None

    context = {"error": error}
    return render(request, "login.html", context)
        


def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the Django admin panel
            return redirect(reverse("admin:index"))
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "signup.html", context)

class UserViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user.role.role)
        if self.request.user.role.role == UserWithRole.Role.MANAGEMENT:
            return User.objects.all()
        # else return only the user itself
        else:
            return User.objects.filter(id=self.request.user.id)

class UserWithRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/users/" API endpoint
    """

    serializer_class = UserWithRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(self.request.user.role.role)
        if self.request.user.role.role == UserWithRole.Role.MANAGEMENT:
            return UserWithRole.objects.all()
        # else return only the user itself
        else:
            return UserWithRole.objects.filter(id=self.request.user.id)


def user_view(request):
    if request.method == "GET":
        user = request.user
        return JsonResponse({"username": user.username, "role": user.role.role})
    else:
        return JsonResponse({"error": "Invalid request method."})

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/clients/" API endpoint
    """

    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, ClientPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "company_name"]
    filterset_fields = ["existing_client", "first_name", "company_name"]
    ordering_fields = ["first_name", "company_name"]

    def get_queryset(self):
        # for different roles, adjust accordingly
        # also ensure you have role field in your UserWithRole model

        # if it's a sales role
        if self.request.user.role.role == UserWithRole.Role.SALES:
            return Client.objects.filter(sales_contact=self.request.user)

        # if it's a support role
        elif self.request.user.role.role == UserWithRole.Role.SUPPORT:
            return Client.objects.filter(
                event__sales_contact=self.request.user
            )

        # if it's a management role
        elif self.request.user.role.role == UserWithRole.Role.MANAGEMENT:
            return Client.objects.all()


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/contracts/" API endpoint
    """

    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, ContractPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "contract_date",
        "price",
    ]
    filterset_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "client__phone_number",
        "price",
    ]

    def get_queryset(self):
        # adjust this for your roles
        # ensure you have role field in your UserWithRole model

        # if it's a sales role
        if self.request.user.role.role == UserWithRole.Role.SALES:
            return Contract.objects.filter(associated_team_member=self.request.user)

        # if it's a support role
        elif self.request.user.role.role == UserWithRole.Role.SUPPORT:
            return Contract.objects.filter(
                event__associated_team_member=self.request.user
            )

        # if it's a management role
        elif self.request.user.role.role == UserWithRole.Role.MANAGEMENT:
            return Contract.objects.all()


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/events/" API endpoint
    """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, EventPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "event_date",
        "finished",
    ]
    filterset_fields = [
        "client__first_name",
        "client__last_name",
        "client__email",
        "event_date",
        "finished",
    ]

    def get_queryset(self):
        # adjust this for your roles
        # ensure you have role field in your UserWithRole model

        # if it's a sales role
        if self.request.user.role.role == UserWithRole.Role.SALES:
            return Event.objects.filter(associated_team_member=self.request.user)

        # if it's a support role
        elif self.request.user.role.role == UserWithRole.Role.SUPPORT:
            return Event.objects.filter(associated_team_member=self.request.user)

        # if it's a management role
        elif self.request.user.role.role == UserWithRole.Role.MANAGEMENT:
            return Event.objects.all()
