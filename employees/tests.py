from datetime import date

from django.contrib.auth.models import User, Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department, Employee


class EmployeePermissionTests(APITestCase):

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

        self.manager_user = User.objects.create_user(
            username="manager1", password="TestPass123!"
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

        manager_group, _ = Group.objects.get_or_create(name="Manager")

        self.hr_user.groups.add(hr_group)
        self.manager_user.groups.add(manager_group)

        self.employee_url = reverse("employee-list")

    def test_employee_can_see_only_own_profile(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.get(self.employee_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]["employee_id"], "EMP001")

    def test_hr_admin_can_see_all_employees(self):
        self.client.force_authenticate(user=self.hr_user)

        response = self.client.get(self.employee_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

    def test_manager_can_see_all_employees(self):
        self.client.force_authenticate(user=self.manager_user)

        response = self.client.get(self.employee_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)


def test_employee_cannot_update_other_employee(self):
    self.client.force_authenticate(user=self.employee_user)

    url = reverse("employee-detail", kwargs={"pk": self.other_employee.id})

    response = self.client.patch(url, {"designation": "HR Manager"}, format="json")

    self.assertIn(
        response.status_code,
        [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        ],
    )

    self.other_employee.refresh_from_db()

    self.assertEqual(self.other_employee.designation, "Software Engineer")

    def test_unauthenticated_user_cannot_access_employees(self):
        response = self.client.get(self.employee_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
