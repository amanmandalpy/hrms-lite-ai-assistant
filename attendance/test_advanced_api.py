from datetime import date

from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department, Employee
from attendance.models import Attendance


class AttendanceAdvancedAPITests(APITestCase):

    def setUp(self):
        self.employee_user = User.objects.create_user(
            username="employee1", password="TestPass123!"
        )

        self.other_user = User.objects.create_user(
            username="employee2", password="TestPass123!"
        )

        self.hr_user = User.objects.create_user(
            username="hradmin", password="TestPass123!"
        )

        self.department = Department.objects.create(name="Engineering")

        self.employee = Employee.objects.create(
            user=self.employee_user,
            employee_id="EMP001",
            department=self.department,
            designation="Python Developer",
            date_of_joining=date.today(),
        )

        self.other_employee = Employee.objects.create(
            user=self.other_user,
            employee_id="EMP002",
            department=self.department,
            designation="Software Engineer",
            date_of_joining=date.today(),
        )

        hr_group, _ = Group.objects.get_or_create(name="HR Admin")
        self.hr_user.groups.add(hr_group)

        self.url = reverse("attendance-list")

    def test_hr_admin_can_create_attendance(self):
        self.client.force_authenticate(user=self.hr_user)

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "date": str(date.today()),
                "status": "present",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        attendance = Attendance.objects.get(employee=self.employee, date=date.today())

        self.assertEqual(attendance.recorded_by, self.hr_user)

    def test_employee_cannot_update_attendance(self):
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            status="present",
            recorded_by=self.hr_user,
        )

        self.client.force_authenticate(user=self.employee_user)

        detail_url = reverse("attendance-detail", kwargs={"pk": attendance.id})

        response = self.client.patch(detail_url, {"status": "absent"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        attendance.refresh_from_db()

        self.assertEqual(attendance.status, "present")


def test_employee_cannot_see_other_employee_attendance(self):

    # Create own attendance
    Attendance.objects.create(
        employee=self.employee,
        date=date.today(),
        status="present",
        recorded_by=self.hr_user,
    )

    # Create another employee's attendance
    Attendance.objects.create(
        employee=self.other_employee,
        date=date.today(),
        status="present",
        recorded_by=self.hr_user,
    )

    self.client.force_authenticate(user=self.employee_user)

    response = self.client.get(self.url)

    self.assertEqual(response.status_code, status.HTTP_200_OK)

    employee_ids = [item["employee"] for item in response.data]

    self.assertIn(self.employee.id, employee_ids)

    self.assertNotIn(self.other_employee.id, employee_ids)


class AttendanceDatabaseConstraintTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="employee1", password="TestPass123!"
        )

        self.hr_user = User.objects.create_user(
            username="hradmin", password="TestPass123!"
        )

        self.department = Department.objects.create(name="Engineering")

        self.employee = Employee.objects.create(
            user=self.user,
            employee_id="EMP001",
            department=self.department,
            designation="Python Developer",
            date_of_joining=date.today(),
        )

        self.attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            status="present",
            recorded_by=self.hr_user,
        )

    def test_duplicate_attendance_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Attendance.objects.create(
                    employee=self.employee,
                    date=date.today(),
                    status="absent",
                    recorded_by=self.hr_user,
                )

        self.assertEqual(
            Attendance.objects.filter(
                employee=self.employee, date=date.today()
            ).count(),
            1,
        )
