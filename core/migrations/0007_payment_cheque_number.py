# Generated by Django 5.0.3 on 2024-03-09 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_organizationconfig_contact_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='cheque_number',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
