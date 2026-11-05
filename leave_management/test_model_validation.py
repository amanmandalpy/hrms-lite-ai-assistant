from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from employees.models import Department, Employee
from leave_management.models import LeaveRequest


class LeaveModelValidationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="employee1", password="TestPass123!"
        )

        self.department = Department.objects.create(name="Engineering")

        self.employee = Employee.objects.create(
            user=self.user,
            employee_id="EMP001",
            department=self.department,
            designation="Python Developer",
            date_of_joining=date.today(),
        )

    def test_end_date_cannot_be_before_start_date(self):
        leave = LeaveRequest(
            employee=self.employee,
            leave_type="casual",
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=2),
            reason="Personal work",
        )

        with self.assertRaises(ValidationError):
            leave.full_clean()

    def test_leave_cannot_start_in_past(self):
        yesterday = date.today() - timedelta(days=1)

        leave = LeaveRequest(
            employee=self.employee,
            leave_type="casual",
            start_date=yesterday,
            end_date=yesterday,
            reason="Personal work",
        )

        with self.assertRaises(ValidationError):
            leave.full_clean()

    def test_valid_leave_passes_model_validation(self):
        leave = LeaveRequest(
            employee=self.employee,
            leave_type="casual",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=3),
            reason="Personal work",
        )

        leave.full_clean()

    def test_leave_string_representation(self):
        leave = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type="casual",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=3),
            reason="Personal work",
        )

        expected = f"EMP001: casual " f"({leave.start_date} to {leave.end_date})"

        self.assertEqual(str(leave), expected)
