from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class UserWithRole(models.Model):
    class Role(models.IntegerChoices):
        SALES = 1, "Sales"
        MANAGEMENT = 2, "Management"
        SUPPORT = 3, "Support"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role")
    role = models.IntegerField(choices=Role.choices)


class Client(models.Model):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    existing_client = models.BooleanField(default=False)
    sales_contact = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name}: {self.first_name} {self.last_name} ({self.email}), actual customer: {self.existing_client}"



class Event(models.Model):
    client = models.ForeignKey(
        to=Client, on_delete=models.CASCADE, null=True, blank=True
    )
    contract = models.ForeignKey(
        to="Contract",
        on_delete=models.CASCADE,
        related_name="event_contract",
    )
    support_contact = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True, blank=True
    )
    attendees = models.IntegerField(null=True, blank=True)
    event_name = models.CharField(max_length=255)
    event_date = models.DateField()
    event_location = models.CharField(max_length=255)
    # set a default valid value for the dates to apply the migration
    date_created = models.DateTimeField(default=timezone.now, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    notes= models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False, verbose_name="Event completed?")
    # ...


class Contract(models.Model):
    event = models.ForeignKey(
        to=Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="contract_event",
    )
    client = models.ForeignKey(
        to=Client, on_delete=models.CASCADE, null=True, blank=True
    )
    sales_contact = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True, blank=True
    )
    contract_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False, verbose_name="Contract signed?")
    payment_due = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now, blank=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client} - {self.price}€ - signed: {self.status}"

    # ...
