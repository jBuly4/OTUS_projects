# Generated by Django 4.2.3 on 2023-07-24 19:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hasker_app', '0014_alter_postquestion_options_alter_postanswer_publish_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='postquestion',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='postanswer',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 24, 19, 57, 9, 703245, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='postquestion',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 24, 19, 57, 9, 702363, tzinfo=datetime.timezone.utc)),
        ),
    ]