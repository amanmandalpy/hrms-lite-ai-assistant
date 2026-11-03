from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Department, Employee
from .serializers import DepartmentSerializer, EmployeeSerializer
from accounts.permissions import IsHRAdmin


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsHRAdmin()]

        return [IsAuthenticated()]


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Employee.objects.select_related(
            "user",
            "department",
        )

        if (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        ):
            return queryset.all()

        return queryset.filter(user=user)

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsHRAdmin()]

        return [IsAuthenticated()]
