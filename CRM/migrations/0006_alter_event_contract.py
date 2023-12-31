# Generated by Django 4.2.1 on 2023-06-29 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("CRM", "0005_alter_contract_sales_contact"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="contract",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event_contract",
                to="CRM.contract",
            ),
            preserve_default=False,
        ),
    ]
