from django.contrib import admin
from .models import LeaveRequest

# Register your models here.

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
        "created_at",
    )

    list_filter = ("status", "leave_type", "start_date")
    search_fields = (
        "employee_employee_id",
        "employee_user_username",
    )
    readonly_fields = ("created_at", "updated_at")
