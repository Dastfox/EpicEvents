from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from CRM.models import Client, Contract, Event

from CRM.models import UserWithRole

DICT_CLIENT = {
    "first_name": "Test Client",
    "last_name": "Test",
    "email": "test@test.com",
    "phone": "0639168000000",
    "mobile": "1234567890",
    "company_name": "Test Company",
}

DICT_CONTRACT = {
    "client": None,
    "sales_contact": None,
    "price": "100.00",
    "status": False,
    "payment_due": "2023-07-02",
}

DICT_EVENT = {
    "client": None,
    "contract": None,
    "support_contact": None,
    "attendees": 10,
    "event_name": "Test Event",
    "event_date": "2023-07-02",
    "event_location": "Test Location",
    "notes": "Test notes",
    "status": False,
}


class PermissionsTestClient(TestCase):
    def setUp(self):
        self.management_user = User.objects.create_user(
            username="test_management", password="test_password"
        )
        UserWithRole.objects.create(user=self.management_user, role=2)

        self.sales_user = User.objects.create_user(
            username="test_sales", password="test_password"
        )
        UserWithRole.objects.create(user=self.sales_user, role=1)

        self.support_user = User.objects.create_user(
            username="test_support", password="test_password"
        )
        UserWithRole.objects.create(user=self.support_user, role=3)

        self.client = APIClient()

    def test_management_user_permissions(self):
        # set up
        self.client.force_authenticate(user=self.sales_user)
        DICT_CLIENT.update({"sales_contact": self.sales_user.id})

        response = self.client.post("/clients/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_id = response.data.get("id")

        response = self.client.put(f"/clients/{self.client_id}/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/clients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_user_permissions(self):
        # set up
        self.client.force_authenticate(user=self.sales_user)
        DICT_CLIENT.update({"sales_contact": self.sales_user.id})

        response = self.client.post("/clients/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_id = response.data.get("id")

        DICT_CLIENT.update({"sales_contact": ""})

        response = self.client.put(f"/clients/{self.client_id}/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"/clients/{self.client_id}/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get("/clients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_support_user_permissions(self):
        # set up
        self.client.force_authenticate(user=self.sales_user)
        DICT_CLIENT.update({"sales_contact": self.sales_user.id})

        response = self.client.post("/clients/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_id = response.data.get("id")

        DICT_CLIENT.update({"sales_contact": ""})

        response = self.client.put(f"/clients/{self.client_id}/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"/clients/{self.client_id}/", data=DICT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get("/clients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionsTestContract(TestCase):
    def setUp(self):
        self.management_user = User.objects.create_user(
            username="test_management", password="test_password"
        )
        UserWithRole.objects.create(user=self.management_user, role=2)

        self.sales_user = User.objects.create_user(
            username="test_sales", password="test_password"
        )
        UserWithRole.objects.create(user=self.sales_user, role=1)

        self.support_user = User.objects.create_user(
            username="test_support", password="test_password"
        )
        UserWithRole.objects.create(user=self.support_user, role=3)

        self.client_obj = Client.objects.create(
            first_name="Test Client",
            last_name="Test",
            email="test@test.com",
            phone="0639168000000",
            mobile="1234567890",
            company_name="Test Company",
            sales_contact=self.sales_user,
        )

        self.client = APIClient()

    def test_management_user_permissions(self):
        self.client_id = self.client_obj.id

        DICT_CONTRACT.update(
            {"client": self.client_id, "sales_contact": self.sales_user.id}
        )

        self.client.force_authenticate(user=self.management_user)
        response = self.client.post("/contracts/", data=DICT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.contract_id = response.data.get("id")

        response = self.client.put(
            f"/contracts/{self.contract_id}/", data=DICT_CONTRACT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get("/contracts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_user_permissions(self):
        self.client_id = self.client_obj.id

        DICT_CONTRACT.update(
            {"client": self.client_id, "sales_contact": self.sales_user.id}
        )

        self.client.force_authenticate(user=self.sales_user)

        response = self.client.post("/contracts/", data=DICT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.contract_id = response.data.get("id")

        DICT_CONTRACT.update({"sales_contact": ""})

        response = self.client.put(
            f"/contracts/{self.contract_id}/", data=DICT_CONTRACT
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get("/contracts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            f"/contracts/{self.contract_id}/", data=DICT_CONTRACT
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

    def test_support_user_permissions(self):
        self.client_id = self.client_obj.id

        DICT_CONTRACT.update(
            {"client": self.client_id, "sales_contact": self.sales_user.id}
        )
        self.client.force_authenticate(user=self.sales_user)
        response = self.client.post("/contracts/", data=DICT_CONTRACT)
        self.contract_id = response.data.get("id")

        self.client.force_authenticate(user=self.support_user)

        response = self.client.post("/contracts/", data=DICT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        DICT_CONTRACT.update({"sales_contact": ""})

        response = self.client.put(
            f"/contracts/{self.contract_id}/", data=DICT_CONTRACT
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            f"/contracts/{self.contract_id}/", data=DICT_CONTRACT
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        
        response = self.client.get("/contracts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionsTestEvent(TestCase):
    def setUp(self):
        self.management_user = User.objects.create_user(
            username="test_management", password="test_password"
        )
        UserWithRole.objects.create(user=self.management_user, role=2)

        self.sales_user = User.objects.create_user(
            username="test_sales", password="test_password"
        )
        UserWithRole.objects.create(user=self.sales_user, role=1)

        self.support_user = User.objects.create_user(
            username="test_support", password="test_password"
        )
        UserWithRole.objects.create(user=self.support_user, role=3)

        self.client_obj = Client.objects.create(
            first_name="Test Client",
            last_name="Test",
            email="test@test.com",
            phone="0639168000000",
            mobile="1234567890",
            company_name="Test Company",
            sales_contact=self.sales_user,
        )

        self.contract_obj = Contract.objects.create(
            client=self.client_obj,
            sales_contact=self.sales_user,
            price="100.00",
            status=False,
            payment_due="2023-07-02",
        )

        self.client = APIClient()

    def test_management_user_permissions(self):
        self.client_id = self.client_obj.id

        DICT_EVENT.update(
            {
                "client": self.client_id,
                "support_contact": self.support_user.id,
                "contract": self.contract_obj.id,
            }
        )

        self.client.force_authenticate(user=self.management_user)

        response = self.client.post("/events/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.event_id = response.data.get("id")

        response = self.client.put(f"/events/{self.event_id}/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sales_user_permissions(self):
              
        self.client_id = self.client_obj.id

        DICT_EVENT.update(
            {
                "client": self.client_id,
                "support_contact": self.support_user.id,
                "contract": self.contract_obj.id,
            }
        )
        
        self.client.force_authenticate(user=self.support_user)
        response = self.client.post("/events/", data=DICT_EVENT)
        self.event_id = response.data.get("id")
        

        self.client.force_authenticate(user=self.sales_user)

        response = self.client.post("/events/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        response = self.client.put(f"/events/{self.event_id}/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_support_user_permissions(self):
        self.client_id = self.client_obj.id
        
        DICT_EVENT.update(
            {
                "client": self.client_id,
                "support_contact": self.support_user.id,
                "contract": self.contract_obj.id,
            }
        )

        self.client.force_authenticate(user=self.support_user)

        response = self.client.post("/events/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.event_id = response.data.get("id")

        DICT_EVENT.update({"support_contact": ""})

        response = self.client.put(f"/events/{self.event_id}/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"/events/{self.event_id}/", data=DICT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.get("/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
