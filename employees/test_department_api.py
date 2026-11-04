from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department

User = get_user_model()


class DepartmentAPITests(APITestCase):

    def setUp(self):
        self.hr_admin = User.objects.create_user(
            username="hradmin", password="TestPassword123"
        )

        hr_group, _ = Group.objects.get_or_create(name="HR Admin")
        self.hr_admin.groups.add(hr_group)

        self.employee = User.objects.create_user(
            username="employee", password="TestPassword123"
        )

        self.department_url = reverse("department-list")

    def test_unauthenticated_user_cannot_access_departments(self):
        response = self.client.get(self.department_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_employee_can_view_departments(self):
        self.client.force_authenticate(user=self.employee)

        response = self.client.get(self.department_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_create_department(self):
        self.client.force_authenticate(user=self.employee)

        response = self.client.post(
            self.department_url,
            {"name": "Development", "description": "Software Development Team"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(Department.objects.filter(name="Development").exists())

    def test_hr_admin_can_create_department(self):
        self.client.force_authenticate(user=self.hr_admin)

        response = self.client.post(
            self.department_url,
            {"name": "Development", "description": "Software Development Team"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Department.objects.filter(name="Development").exists())
