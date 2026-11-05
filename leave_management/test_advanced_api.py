from datetime import date, timedelta

from django.contrib.auth.models import User, Group
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department, Employee
from leave_management.models import LeaveRequest


class LeaveAdvancedAPITests(APITestCase):

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

    def test_employee_cannot_see_other_employee_leave(self):
        LeaveRequest.objects.create(
            employee=self.other_employee,
            leave_type="sick",
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=6),
            reason="Medical appointment",
        )

        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        employee_ids = [item["employee"] for item in response.data]

        self.assertIn(self.employee.id, employee_ids)
        self.assertNotIn(self.other_employee.id, employee_ids)

    def test_approved_leave_cannot_be_approved_again(self):
        self.client.force_authenticate(user=self.hr_user)

        approve_url = reverse("leave-request-approve", kwargs={"pk": self.leave.id})

        first_response = self.client.post(approve_url)
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(approve_url)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejected_leave_cannot_be_approved(self):
        self.leave.status = LeaveRequest.LeaveStatus.REJECTED
        self.leave.save()

        self.client.force_authenticate(user=self.hr_user)

        approve_url = reverse("leave-request-approve", kwargs={"pk": self.leave.id})

        response = self.client.post(approve_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_date_range_is_rejected(self):
        self.client.force_authenticate(user=self.employee_user)

        response = self.client.post(
            self.url,
            {
                "leave_type": "casual",
                "start_date": str(date.today() + timedelta(days=5)),
                "end_date": str(date.today() + timedelta(days=2)),
                "reason": "Personal work",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_past_leave_date_is_rejected(self):
        self.client.force_authenticate(user=self.employee_user)

        yesterday = date.today() - timedelta(days=1)

        response = self.client.post(
            self.url,
            {
                "leave_type": "casual",
                "start_date": str(yesterday),
                "end_date": str(yesterday),
                "reason": "Personal work",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_without_employee_profile_cannot_apply_leave(self):
        user_without_profile = User.objects.create_user(
            username="no_profile", password="TestPass123!"
        )

        self.client.force_authenticate(user=user_without_profile)

        response = self.client.post(
            self.url,
            {
                "leave_type": "casual",
                "start_date": str(date.today() + timedelta(days=2)),
                "end_date": str(date.today() + timedelta(days=3)),
                "reason": "Personal work",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hr_admin_can_reject_leave(self):
        self.client.force_authenticate(user=self.hr_user)

        reject_url = reverse("leave-request-reject", kwargs={"pk": self.leave.id})

        response = self.client.post(
            reject_url,
            {"review_comment": "Request rejected"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.leave.refresh_from_db()

        self.assertEqual(self.leave.status, LeaveRequest.LeaveStatus.REJECTED)
        self.assertEqual(self.leave.reviewed_by, self.hr_user)
        self.assertIsNotNone(self.leave.reviewed_at)

    def test_rejected_leave_cannot_be_rejected_again(self):
        self.leave.status = LeaveRequest.LeaveStatus.REJECTED
        self.leave.save()

        self.client.force_authenticate(user=self.hr_user)

        reject_url = reverse("leave-request-reject", kwargs={"pk": self.leave.id})

        response = self.client.post(reject_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
