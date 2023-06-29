import json
from django import forms
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
from django.db.models import Q
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
from rest_framework.decorators import api_view, permission_classes

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", )

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def custom_signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            refresh = RefreshToken.for_user(user)

            response_data = {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            return JsonResponse(response_data, status=200)

        else:
            # If the form is invalid, return the errors as a JSON response
            return JsonResponse(form.errors, status=400)

    else:
        return JsonResponse({"detail": "Invalid request method."}, status=405)
        
        
    
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("admin:index"))
    else:
        form = CustomUserCreationForm()

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
        is_sales, is_support, is_management = get_roles_bool(self.request.user)

        if is_management:
            return Client.objects.all()

        if is_sales and is_support:
            return Client.objects.filter(
                Q(contract__sales_contact=self.request.user)
                | Q(event__sales_contact=self.request.user)
            )

        if is_sales:
            return Client.objects.filter(contract__sales_contact=self.request.user)

        if is_support:
            return Client.objects.filter(event__sales_contact=self.request.user)

        return Client.objects.none()


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
        "client__phone",
        "client__company_name",
        "client__mobile",
        "price",
    ]

    def get_queryset(self):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)

        if is_management:
            return Contract.objects.all()

        if is_sales and is_support:
            return Contract.objects.filter(
                Q(associated_team_member=self.request.user)
                | Q(event__sales_contact=self.request.user)
            )

        if is_sales:
            return Contract.objects.filter(associated_team_member=self.request.user)

        if is_support:
            return Contract.objects.filter(event__sales_contact=self.request.user)

        return Contract.objects.none()



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
        "status",
    ]

    def get_queryset(self):
        # adjust this for your roles
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
                
        print(is_sales, is_support, is_management)
        if is_management:
            return Event.objects.all()

        elif is_sales and is_support:
            return Event.objects.filter(
                Q(contract__sales_contact=self.request.user)
                | Q(sales_contact=self.request.user)
            )
        
        elif is_sales:
            return Event.objects.filter(contract__sales_contact=self.request.user)

        elif is_support:
            return Event.objects.filter(sales_contact=self.request.user)

        return Event.objects.none()  # Return an empty queryset if no role matches the condition



def get_roles_bool (user):
        user_roles = user.role.all()  # Retrieve all UserWithRole instances
        is_sales = False
        is_support = False
        is_management = False
        for role in user_roles:
            if role.role == UserWithRole.Role.SALES:
                is_sales = True
            elif role.role == UserWithRole.Role.SUPPORT:
                is_support = True
            elif role.role == UserWithRole.Role.MANAGEMENT:
                is_management = True
        return is_sales, is_support, is_management
    
    