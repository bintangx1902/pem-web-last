# Generated by Django 3.2.16 on 2023-01-05 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_side', '0009_complaint_is_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='address',
            field=models.TextField(default=''),
        ),
    ]
