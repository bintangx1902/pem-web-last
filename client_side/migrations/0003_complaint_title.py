# Generated by Django 3.2.16 on 2023-01-03 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_side', '0002_complaint_needed_tools'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='title',
            field=models.CharField(default='', max_length=255),
        ),
    ]
