# Generated by Django 4.2.3 on 2023-07-31 18:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hasker_app', '0018_postanswer_users_dislike_postquestion_users_dislike_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postanswer',
            options={'ordering': ['-rating', '-publish']},
        ),
        migrations.AlterField(
            model_name='postanswer',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 31, 18, 47, 15, 423648, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='postquestion',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 7, 31, 18, 47, 15, 422091, tzinfo=datetime.timezone.utc)),
        ),
    ]
