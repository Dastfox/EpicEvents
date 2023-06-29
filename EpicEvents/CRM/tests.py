from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from rest_framework import status
from CRM.models import Client, UserWithRole, Contract, Event
from CRM.views import get_roles_bool


class UserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
    

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)


class ClientTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = Client.objects.create(first_name="Test Client",
                                            last_name="Test",
                                            email="test@test.com",
                                            mobile="1234567890",
                                            company_name="Test Company",
                                            existing_client=True)

    def test_client_creation(self):
        self.assertEqual(Client.objects.count(), 1)


class ContractTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = Client.objects.create(first_name="Test Client",
                                            last_name="Test",
                                            email="test@test.com",
                                            mobile="1234567890",
                                            company_name="Test Company",
                                            existing_client=True)
        self.contract = Contract.objects.create(client=self.client,
                                                contract_date="2023-07-01",
                                                sales_contact=self.user,
                                                price="1000",
                                                payment_due="2023-07-31")

    def test_contract_creation(self):
        self.assertEqual(Contract.objects.count(), 1)


class EventTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = Client.objects.create(first_name="Test Client",
                                            last_name="Test",
                                            email="test@test.com",
                                            mobile="1234567890",
                                            company_name="Test Company",)
        self.contract = Contract.objects.create(client=self.client,
                                                contract_date="2023-07-01",
                                                sales_contact=self.user,
                                                price="1000",
                                                payment_due="2023-07-31")
                                                
        self.event = Event.objects.create(client=self.client,
                                          contract=self.contract,
                                          event_date="2023-07-01",
                                          support_contact=self.user,
                                          status=True)

    def test_event_creation(self):
        self.assertEqual(Event.objects.count(), 1)

class GetRolesBoolTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

    def test_get_roles_bool(self):
        is_sales, is_support, is_management = get_roles_bool(self.user)
        self.assertEqual(is_sales, False)
        self.assertEqual(is_support, False)
        self.assertEqual(is_management, False)


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.c = TestClient()  # Use the renamed import

    def test_login_view(self):
        response = self.c.post('/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

class SignupViewTest(TestCase):
    def setUp(self):
        self.c = TestClient()  # Use the renamed import

    def test_signup_view(self):
        response = self.c.post('/signup/', {'username': 'testuser', 'password1': 'testpassword', 'password2': 'testpassword',
                                            'first_name': 'test', 'last_name': 'test', 'email': 'test@test.com', 'role': 'SALES'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)