from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        CASUAL = "casual", "Casual Leave"
        SICK = "sick", "Sick Leave"
        EARNED = "earned", "Earned Leave"
        UNPAID = "unpaid", "Unpaid Leave"

    class LeaveStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="leave_requests",
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_leave_requests",
        null=True,
        blank=True,
    )
    review_comment = models.CharField(max_length=250, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        errors = {}

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                errors["end_date"] = "End date cannot be earlier than start date."

        if self.start_date and self.start_date < timezone.localdate():
            errors["start_date"] = "Leave cannot start in the past."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.employee.employee_id}: "
            f"{self.leave_type} ({self.start_date} to {self.end_date})"
        )
