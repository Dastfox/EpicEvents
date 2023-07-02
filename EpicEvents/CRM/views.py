from django import forms
from django_filters.rest_framework import DateFilter, FilterSet
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
import sentry_sdk
from .models import User
from django.db.models import Q
from .models import Contract, Client, UserWithRole, Event
from rest_framework_simplejwt.views import TokenObtainPairView
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

from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied


def get_roles_bool(user):
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


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
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
                role_value = next(
                    val for val, name in UserWithRole.Role.choices if name == group_name
                )
                user_with_role, created = UserWithRole.objects.get_or_create(
                    user=instance, role=role_value
                )
                user_with_role.role = role_value
                user_with_role.save()
            except StopIteration:
                print(f"No role found for group: {group_name}")

    elif action == "post_remove":
        # Handle removal from a group
        for group in kwargs.get("pk_set", []):
            group_obj = Group.objects.get(pk=group)
            group_name = group_obj.name
            try:
                role_value = next(
                    val for val, name in UserWithRole.Role.choices if name == group_name
                )
                user_with_role = UserWithRole.objects.filter(
                    user=instance, role=role_value
                )
                if user_with_role.exists():
                    user_with_role.delete()
            except StopIteration:
                sentry_sdk.capture_message(f"No role found for group: {group_name}")
                print(f"No role found for group: {group_name}")


def create_groups_view(request):
    roles = ["Sales", "Management", "Support"]  # Get the list of roles
    for role in roles:
        group, _ = Group.objects.get_or_create(name=role)

    for user_with_role in UserWithRole.objects.all():
        role_name = (
            user_with_role.get_role_display()
        )  # Returns the string representation of the role
        group = Group.objects.get(name=role_name)  # Get the Group object
        user_with_role.user.groups.add(group)  # Add the User object to the group

    return JsonResponse(
        {
            "status": "success",
            "message": "Groups created and users assigned successfully.",
        }
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def custom_signup_view(request):
    if request.method == "POST":
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
    """
    ViewSet for "/users/" API endpoint
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        _, _, is_management = get_roles_bool(self.request.user)
        if is_management:
            return User.objects.all()
        # else return only the user itself
        else:
            return User.objects.filter(id=self.request.user.id)


class UserWithRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/users_with_role/" API endpoint
    """

    serializer_class = UserWithRoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        _, _, is_management = get_roles_bool(self.request.user)
        if is_management:
            return UserWithRole.objects.all()
        # else return only the user itself
        else:
            print(self.request.user.id)
            return UserWithRole.objects.filter(user_id=self.request.user.id)


class ClientFilter(FilterSet):
    class Meta:
        model = Client
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "company_name",
            "mobile",
        ]

class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for "/clients/" API endpoint
    """

    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, ClientPermissions]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "company_name"]
    ordering_fields = ["first_name", "company_name"]
    filterset_class = ClientFilter
    
    def create(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        # Check if the user has the SUPPORT role
        if is_sales or is_management:
            return super().create(request, *args, **kwargs)
        else:
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )
                
            
        
    def update(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        
        if is_management:
            return super().update(request, *args, **kwargs)
        elif is_sales:
            
            if self.get_object().sales_contact != self.request.user:
                JsonResponse(
                    {"detail": "You do not have permission to perform this action."},
                status=403,
                )
            else:
                return super().update(request, *args, **kwargs)
        
        return super().update(request, *args, **kwargs)

        

    def get_queryset(self):
        return Client.objects.all()




class ContractFilter(FilterSet):
    payment_due__gt = DateFilter(field_name='payment_due', lookup_expr='gt')

    class Meta:
        model = Contract
        fields = [
            "client__first_name",
            "client__last_name",
            "client__email",
            "client__phone",
            "client__company_name",
            "client__mobile",
            "price",
            "payment_due",
            "status"
        ]
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
        "payment_due",  
        'status'
    ]
    filterset_class = ContractFilter

    def get_queryset(self):
        return Contract.objects.all()
    
    def create(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        # Check if the user has the SUPPORT role
        if is_sales or is_management:
            return super().create(request, *args, **kwargs)
        else:
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )
                
            
        
    def update(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        
        if is_management:
            return super().update(request, *args, **kwargs)
        else:
            if self.get_object().sales_contact != self.request.user or not is_sales:
                JsonResponse(
                    {"detail": "You do not have permission to perform this action."},
                status=403,
                )
            else:
                return super().update(request, *args, **kwargs)

        



        
    
class EventFilter(FilterSet):
    event_date__gt = DateFilter(field_name='event_date', lookup_expr='gt')

    class Meta:
        model = Event
        fields = [
            "client__first_name",
            "client__last_name",
            "client__email",
            "event_date",
            "status",
            'support_contact'
        ]

    def get_queryset(self):
        return Event.objects.all()

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
        "status",
        'support_contact'
    ]
    filterset_class = EventFilter


    def create(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        # Check if the user has the SUPPORT role
        if not is_support and not is_management:
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )

        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        is_sales, is_support, is_management = get_roles_bool(self.request.user)
        # Check if the user has the SUPPORT role
        if not is_support and not is_management:
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )

        return super().update(request, *args, **kwargs)
    
    def get_queryset(self):
        return Event.objects.all()