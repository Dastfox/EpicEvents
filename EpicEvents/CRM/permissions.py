from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .models import UserWithRole, Client, Contract, Event


class UserWithRolePermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserWithRole.Role.MANAGEMENT:
            return True

        if request.user.role in (UserWithRole.Role.SALES, UserWithRole.Role.SUPPORT):
            return request.user == obj.user
        else:
            raise PermissionDenied("You do not have permission.")


class ClientPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserWithRole.Role.MANAGEMENT:
            print("management")
            return True

        if request.user.role == UserWithRole.Role.SALES and view.action in (
            "create",
            "retrieve",
            "update",
        ):
            return request.user == obj.associated_team_member.user
        elif (
            request.user.role == UserWithRole.Role.SUPPORT and view.action == "retrieve"
        ):
            return Event.objects.filter(
                associated_team_member__user=request.user, client=obj
            ).exists()
        else:
            raise PermissionDenied("You do not have permission.")


class ContractPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserWithRole.Role.MANAGEMENT:
            return True

        if request.user.role == UserWithRole.Role.SALES and view.action in (
            "create",
            "retrieve",
            "update",
        ):
            return request.user == obj.associated_team_member.user
        else:
            raise PermissionDenied("You do not have permission.")


class EventPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == UserWithRole.Role.MANAGEMENT:
            return True

        if request.user.role == UserWithRole.Role.SALES and view.action in (
            "create",
            "retrieve",
            "update",
        ):
            return request.user == obj.associated_team_member.user
        elif request.user.role == UserWithRole.Role.SUPPORT and view.action in (
            "retrieve",
            "update",
        ):
            return request.user == obj.associated_team_member.user
        else:
            raise PermissionDenied("You do not have permission.")
