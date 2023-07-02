from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Client, Contract, Event

from CRM.models import UserWithRole

DATAPOST_CLIENT = {
    "first_name": "Test Client",
    "last_name": "Test",
    "email": "test@test.com",
    "phone": "0639168000000",
    "mobile": "1234567890",
    "company_name": "Test Company",
}

DATAPUT_CLIENT = {
    "first_name": "Test Client PUT",
    "last_name": "Test",
    "email": "test@test.com",
    "phone": "0639168000000",
    "mobile": "1234567890",
    "company_name": "Test Company",
    "sales_contact": "",
}

DATAPOST_CONTRACT = {
    "client": None,
    "sales_contact": None,
    "price": "100.00",
    "status": False,
    "payment_due": "2023-07-02",
}

DATAPUT_CONTRACT = {
    "client": None,
    "sales_contact": None,
    "price": "101.00",
    "status": False,
    "payment_due": "2023-07-02",
}

DATAPOST_EVENT= {
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

DATAPUT_EVENT = {
    "client": None,
    "contract": None,
    "support_contact": None,
    "attendees": 20,
    "event_name": "Test Event PUT",
    "event_date": "2023-07-03",
    "event_location": "Test Location PUT",
    "notes": "Test notes PUT",
    "status": True,
}


class PermissionsTest(TestCase):
    event_id = None
    client_id = None
    contract_id = None

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

    def test_permissions_client(self):
        self.client.force_authenticate(user=self.sales_user)
        DATAPOST_CLIENT.update({"sales_contact": self.sales_user.id})

        # Test management user permissions
        self.client.force_authenticate(user=self.management_user)

        print(DATAPUT_CLIENT)
        response = self.client.post("/clients/", data=DATAPOST_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_id = response.data.get("id")

        response = self.client.put(f"/clients/{self.client_id}/", data=DATAPUT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test sales user permissions
        self.client.force_authenticate(user=self.sales_user)
        DATAPOST_CLIENT.update({"sales_contact": self.sales_user.id})

        response = self.client.post("/clients/", data=DATAPOST_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_id = response.data.get("id")

        response = self.client.put(f"/clients/{self.client_id}/", data=DATAPUT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(f"/clients/{self.client_id}/", data=DATAPUT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test support user permissions
        self.client.force_authenticate(user=self.support_user)
        DATAPOST_CLIENT.update({"sales_contact": self.sales_user.id})

        DATAPUT_CLIENT.update({"sales_contact": ""})
        response = self.client.post("/clients/", data=DATAPOST_CLIENT)

        response = self.client.put(f"/clients/{self.client_id}/", data=DATAPUT_CLIENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_contract(self):
        self.client.force_authenticate(user=self.sales_user)
        DATAPOST_CLIENT.update({"sales_contact": self.sales_user.id})
        # Test management user permissions
        self.client.force_authenticate(user=self.management_user)
        response = self.client.post("/clients/", data=DATAPOST_CLIENT)

        client_id = response.data.get("id")

        DATAPOST_CONTRACT.update(
            {"client": client_id, "sales_contact": self.sales_user.id}
        )
        DATAPUT_CONTRACT.update(
            {"client": client_id, "sales_contact": self.sales_user.id}
        )

        response = self.client.post("/contracts/", data=DATAPOST_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contract_id = response.data.get("id")

        response = self.client.put(f"/contracts/{contract_id}/", data=DATAPUT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test sales user permissions
        self.client.force_authenticate(user=self.sales_user)

        response = self.client.post("/contracts/", data=DATAPOST_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"/contracts/{contract_id}/", data=DATAPUT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test support user permissions
        self.client.force_authenticate(user=self.support_user)

        response = self.client.post("/contracts/", data=DATAPOST_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(f"/contracts/{contract_id}/", data=DATAPUT_CONTRACT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_permissions(self):
        self.client.force_authenticate(user=self.sales_user)
        DATAPOST_CLIENT.update({"sales_contact": self.sales_user.id})
        # Test management user permissions
        self.client.force_authenticate(user=self.management_user)
        response = self.client.post("/clients/", data=DATAPOST_CLIENT)
        client_id = response.data.get("id")
        DATAPOST_CONTRACT.update(
            {"client": client_id, "sales_contact": self.sales_user.id}
        )
        contract_id = response.data.get("id")
        response = self.client.post("/contracts/", data=DATAPOST_CONTRACT)
        self.client.force_authenticate(user=self.support_user)
        DATAPOST_EVENT.update(
            {
                "contract": contract_id,
                "client": client_id,
                "support_contact": self.support_user.id,
            }
        )
        DATAPUT_EVENT.update(
            {
                "contract": contract_id,
                "client": client_id,
                "support_contact": self.support_user.id,
            }
        )

        self.client.force_authenticate(user=self.management_user)

        response = self.client.post("/events/", data=DATAPOST_EVENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        event_id = response.data.get("id")

        print(DATAPUT_EVENT)
        response = self.client.put(f"/events/{event_id}/", data=DATAPUT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.sales_user)

        response = self.client.post("/events/", data=DATAPOST_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        DATAPUT_EVENT.update({"support_contact": ""})

        response = self.client.put(f"/events/{event_id}/", data=DATAPUT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        
        response = self.client.put(f"/events/{event_id}/", data=DATAPUT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.support_user)

        response = self.client.post("/events/", data=DATAPOST_EVENT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"/events/{event_id}/", data=DATAPUT_EVENT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
