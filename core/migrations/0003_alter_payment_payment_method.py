# Generated by Django 5.0.2 on 2024-02-29 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_paymentreceipt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('Money Money', 'Mobile_Money'), ('Bank', 'Bank'), ('Cash', 'Cash')], default='Bank', max_length=200),
        ),
    ]
