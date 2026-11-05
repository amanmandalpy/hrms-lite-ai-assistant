from datetime import date

from django.contrib.auth.models import User, Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department, Employee
from attendance.models import Attendance


class AttendanceAPITest(APITestCase):

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

        self.hr_group, _ = Group.objects.get_or_create(name="HR Admin")
        self.hr_user.groups.add(self.hr_group)

        self.attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            status="present",
            recorded_by=self.hr_user,
        )

        self.url = reverse("attendance-list")

    def test_unauthenticated_user_cannot_access_attendance(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_can_see_only_own_attendance(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["employee"], self.employee.id)

    def test_employee_cannot_create_attendance(self):
        self.client.force_authenticate(user=self.employee_user)

        payload = {
            "employee": self.employee.id,
            "date": str(date.today()),
            "status": "present",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_admin_can_create_attendance(self):
        self.client.force_authenticate(user=self.hr_user)

        payload = {
            "employee": self.other_employee.id,
            "date": str(date.today()),
            "status": "present",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
