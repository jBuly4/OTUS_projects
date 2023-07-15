# Generated by Django 4.2.3 on 2023-07-15 12:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hasker_app', '0002_postanswer_for_slug_alter_postanswer_publish_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postanswer',
            name='for_slug',
        ),
        migrations.RemoveField(
            model_name='postanswer',
            name='slug',
        ),
        migrations.AlterField(
            model_name='postanswer',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 15, 12, 11, 47, 744351, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='postquestion',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 15, 12, 11, 47, 743740, tzinfo=datetime.timezone.utc)),
        ),
    ]
