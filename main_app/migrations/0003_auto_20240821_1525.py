# Generated by Django 3.1.1 on 2024-08-21 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20240821_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='student_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
