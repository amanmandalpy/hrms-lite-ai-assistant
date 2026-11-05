from io import StringIO

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import TestCase


class SetupRolesCommandTests(TestCase):

    def run_setup_command(self):
        output = StringIO()
        call_command("setup_roles", stdout=output)
        return output.getvalue()

    def test_command_creates_all_three_groups(self):
        self.run_setup_command()

        self.assertTrue(Group.objects.filter(name="HR Admin").exists())

        self.assertTrue(Group.objects.filter(name="Employee").exists())

        self.assertTrue(Group.objects.filter(name="Manager").exists())

    def test_command_assigns_correct_permissions(self):
        self.run_setup_command()

        hr_admin = Group.objects.get(name="HR Admin")
        employee = Group.objects.get(name="Employee")
        manager = Group.objects.get(name="Manager")

        # HR Admin permissions
        self.assertTrue(
            hr_admin.permissions.filter(codename="view_department").exists()
        )

        self.assertTrue(hr_admin.permissions.filter(codename="add_employee").exists())

        # Employee permission
        self.assertTrue(
            employee.permissions.filter(codename="add_leaverequest").exists()
        )

        # Manager permissions
        self.assertTrue(
            manager.permissions.filter(codename="view_leaverequest").exists()
        )

        self.assertTrue(
            manager.permissions.filter(codename="change_leaverequest").exists()
        )

    def test_running_command_twice_does_not_create_duplicate_groups(self):
        self.run_setup_command()
        self.run_setup_command()

        self.assertEqual(Group.objects.count(), 3)
