from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from employees.models import Department, Employee
from attendance.models import Attendance
from leave_management.models import LeaveRequest


class Command(BaseCommand):
    help = "Create HRMS role groups and assign permissions"

    def handle(self, *args, **options):
        hr_admin, _ = Group.objects.get_or_create(name="HR Admin")
        employee, _ = Group.objects.get_or_create(name="Employee")
        manager, _ = Group.objects.get_or_create(name="Manager")

        models_and_permissions = [
            (Department, ["view_department", "add_department", "change_department"]),
            (Employee, ["view_employee", "add_employee", "change_employee"]),
            (Attendance, ["view_attendance", "add_attendance", "change_attendance"]),
            (
                LeaveRequest,
                ["view_leaverequest", "add_leaverequest", "change_leaverequest"],
            ),
        ]

        for model, codenames in models_and_permissions:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(
                content_type=content_type,
                codename__in=codenames,
            )
            hr_admin.permissions.add(*permissions)

        leave_content_type = ContentType.objects.get_for_model(LeaveRequest)

        employee_permission = Permission.objects.filter(
            content_type=leave_content_type,
            codename="add_leaverequest",
        )
        employee.permissions.add(*employee_permission)

        manager_permissions = Permission.objects.filter(
            content_type=leave_content_type,
            codename__in=["view_leaverequest", "change_leaverequest"],
        )
        manager.permissions.add(*manager_permissions)

        self.stdout.write(
            self.style.SUCCESS("HR Admin, Employee, and Manager groups configured.")
        )
