# Generated by Django 5.0.6 on 2024-06-03 02:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upper_info', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='upper_info',
            name='video_url',
            field=models.URLField(default=django.utils.timezone.now),
        ),
    ]