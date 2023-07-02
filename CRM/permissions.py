from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import UserWithRole, Client, Contract, Event


class UserWithRolePermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user_roles = UserWithRole.objects.filter(user=request.user)
        role_numbers = [user_role.role for user_role in user_roles]

        if UserWithRole.Role.MANAGEMENT in role_numbers:
            return True

        if (
            UserWithRole.Role.SALES in role_numbers
            or UserWithRole.Role.SUPPORT in role_numbers
        ):
            return request.user.id == obj.user.id
        raise PermissionDenied("You do not have permission.")


class ClientPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Client):
        user_roles = UserWithRole.objects.filter(user=request.user)
        role_numbers = [user_role.role for user_role in user_roles]

        if UserWithRole.Role.MANAGEMENT in role_numbers:
            return True

        if UserWithRole.Role.SALES in role_numbers and view.action in (
            "create",
            "retrieve",
            "update",
        ):
            return request.user == obj.sales_contact

        if UserWithRole.Role.SUPPORT in role_numbers and view.action == "retrieve":
            return Event.objects.filter(
                sales_contact__user=request.user, client=obj
            ).exists()

      
        raise PermissionDenied("You do not have permission.")


class ContractPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Contract):
        user_roles = UserWithRole.objects.filter(user=request.user)
        role_numbers = [user_role.role for user_role in user_roles]

        if UserWithRole.Role.MANAGEMENT in role_numbers:
            return True

        if UserWithRole.Role.SALES in role_numbers and view.action in (
            "retrieve",
            "update",
        ):
            return request.user == obj.sales_contact

        raise PermissionDenied("You do not have permission.")


class EventPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Event):
        user_roles = UserWithRole.objects.filter(user=request.user)
        role_numbers = [user_role.role for user_role in user_roles]

        if UserWithRole.Role.MANAGEMENT in role_numbers:
            return True

        if UserWithRole.Role.SALES in role_numbers and view.action in (
            "create",
            "retrieve",
            "update",
        ):
            return request.user == obj.support_contact

        if UserWithRole.Role.SUPPORT in role_numbers and view.action in (
            "retrieve",
            "update",
        ):
            return request.user == obj.support_contact
        raise PermissionDenied("You do not have permission.")
