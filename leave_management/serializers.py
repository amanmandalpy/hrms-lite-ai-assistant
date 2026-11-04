from django.utils import timezone
from rest_framework import serializers

from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source="employee.user.get_full_name",
        read_only=True,
    )

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "reviewed_by",
            "review_comment",
            "reviewed_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "employee",
            "status",
            "reviewed_by",
            "review_comment",
            "reviewed_at",
            "created_at",
        ]

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )

        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None),
        )

        if (
            start_date
            and (self.instance is None or "start_date" in attrs)
            and start_date < timezone.localdate()
        ):
            raise serializers.ValidationError(
                {"start_date": "Leave cannot start in the past."}
            )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )

        return attrs
