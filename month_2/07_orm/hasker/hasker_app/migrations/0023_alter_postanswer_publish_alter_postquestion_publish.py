# Generated by Django 4.2.3 on 2023-08-06 12:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hasker_app', '0022_alter_postanswer_publish_alter_postquestion_publish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postanswer',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 8, 6, 12, 46, 43, 615757, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='postquestion',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 8, 6, 12, 46, 43, 614215, tzinfo=datetime.timezone.utc)),
        ),
    ]
