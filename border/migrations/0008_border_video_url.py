# Generated by Django 5.0.6 on 2024-06-03 00:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('border', '0007_border_싫어요_border_좋아요'),
    ]

    operations = [
        migrations.AddField(
            model_name='border',
            name='video_url',
            field=models.URLField(default=django.utils.timezone.now),
        ),
    ]
