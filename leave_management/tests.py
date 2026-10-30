from datetime import date, timedelta

from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from employees.models import Department, Employee
from leave_management.models import LeaveRequest


class LeaveRequestAPITest(APITestCase):

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

        self.leave = LeaveRequest.objects.create(
            employee=self.employee,
            leave_type="casual",
            start_date=date.today() + timedelta(days=2),
            end_date=date.today() + timedelta(days=3),
            reason="Personal work",
        )

        self.url = reverse("leave-request-list")

    def test_unauthenticated_user_cannot_access_api(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_sees_only_own_leave_requests(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["employee"], self.employee.id)

    def test_employee_cannot_approve_leave(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.post(
            reverse("leave-request-approve", kwargs={"pk": self.leave.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_can_approve_leave(self):
        self.client.force_authenticate(user=self.hr_user)

        response = self.client.post(
            reverse("leave-request-approve", kwargs={"pk": self.leave.id}),
            {"review_comment": "Approved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.leave.refresh_from_db()

        self.assertEqual(self.leave.status, LeaveRequest.LeaveStatus.APPROVED)
