# Generated by Django 5.0.2 on 2024-03-01 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_class_unique_classes_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('Mobile Money', 'Mobile_Money'), ('Bank', 'Bank'), ('Cash', 'Cash')], default='Bank', max_length=200),
        ),
    ]
