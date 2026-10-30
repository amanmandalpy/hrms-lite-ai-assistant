from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from accounts.permissions import IsHRAdminOrManager
from employees.models import Employee
from rest_framework.exceptions import PermissionDenied

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = LeaveRequest.objects.select_related(
            "employee",
            "employee__user",
            "reviewed_by",
        )

        if (
            user.is_superuser
            or user.groups.filter(name__in=["HR Admin", "Manager"]).exists()
        ):
            return queryset

        return queryset.filter(employee__user=user)

    def perform_create(self, serializer):
        employee = Employee.objects.filter(
            user=self.request.user
        ).first()

        if employee is None:
            raise PermissionDenied(
                "No employee profile found for this user."
            )

        serializer.save(employee=employee)

    def get_permissions(self):
        if self.action in ["approve", "reject"]:
            return [IsHRAdminOrManager()]

        return [permission() for permission in self.permission_classes]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        leave = self.get_object()

        if leave.status != LeaveRequest.LeaveStatus.PENDING:
            return Response(
                {"error": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = LeaveRequest.LeaveStatus.APPROVED
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.review_comment = request.data.get("review_comment", "")
        leave.save()

        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        leave = self.get_object()

        if leave.status != LeaveRequest.LeaveStatus.PENDING:
            return Response(
                {"error": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = LeaveRequest.LeaveStatus.REJECTED
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.review_comment = request.data.get("review_comment", "")
        leave.save()

        return Response(self.get_serializer(leave).data)
