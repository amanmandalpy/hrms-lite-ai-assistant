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
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")

        return attrs
