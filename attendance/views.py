from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsHRAdminOrManager


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = Attendance.objects.select_related(
            "employee",
            "employee__user",
            "recorded_by",
        )

        if (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        ):
            return queryset

        return queryset.filter(employee__user=user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsHRAdminOrManager()]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
