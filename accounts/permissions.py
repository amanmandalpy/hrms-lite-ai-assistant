from rest_framework.permissions import BasePermission


class IsHRAdminOrManager(BasePermission):
    message = "Only HR Admin or Manager can perform this action."

    def has_permission(self, request, view):
        user = request.user

        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        )


class IsEmployeeOrHRManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        ):
            return True

        return obj.employee.user_id == user.id
