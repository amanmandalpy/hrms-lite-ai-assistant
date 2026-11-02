from rest_framework.permissions import BasePermission


class IsHRAdmin(BasePermission):
    message = "Only HR Admin can perform this action."

    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name="HR Admin").exists()
        )


class IsHRAdminOrManager(BasePermission):
    message = "Only HR Admin or Manager can perform this action."

    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        )
