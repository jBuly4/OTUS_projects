# Generated by Django 4.2.3 on 2023-08-06 12:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hasker_app', '0023_alter_postanswer_publish_alter_postquestion_publish'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='postanswer',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 8, 6, 12, 51, 2, 672013, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='postquestion',
            name='publish',
            field=models.DateField(default=datetime.datetime(2023, 8, 6, 12, 51, 2, 670412, tzinfo=datetime.timezone.utc)),
        ),
    ]
