# Generated by Django 4.2.1 on 2023-06-25 11:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("CRM", "0003_rename_associated_team_member_client_sales_contact_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="sales_contact",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
