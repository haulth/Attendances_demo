# Generated by Django 3.1.1 on 2024-09-11 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0021_auto_20240910_1629'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='session',
        ),
        migrations.AddField(
            model_name='student',
            name='subjects',
            field=models.ManyToManyField(to='main_app.Subject'),
        ),
    ]
