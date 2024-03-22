# Generated by Django 5.0.3 on 2024-03-22 10:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_feearrear_arrearpayment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentreceipt',
            name='arrear_payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.arrearpayment'),
        ),
        migrations.AddField(
            model_name='paymentreceipt',
            name='details',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentreceipt',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.payment'),
        ),
        migrations.AlterField(
            model_name='paymentreceipt',
            name='purpose',
            field=models.TextField(blank=True, null=True),
        ),
    ]
