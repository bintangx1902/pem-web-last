# Generated by Django 3.2.16 on 2023-01-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
        ('client_side', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='needed_tools',
            field=models.ManyToManyField(blank=True, null=True, to='company.Tools'),
        ),
    ]
