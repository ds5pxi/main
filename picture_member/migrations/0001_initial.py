# Generated by Django 5.0.6 on 2024-05-30 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Picture_member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('제목', models.CharField(max_length=255)),
                ('작성자', models.CharField(max_length=255)),
                ('내용', models.TextField()),
                ('작성일', models.DateTimeField()),
                ('수정일', models.DateTimeField()),
                ('조회수', models.IntegerField()),
                ('댓글수', models.IntegerField(default=0)),
                ('좋아요', models.IntegerField(default=0)),
                ('싫어요', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture_member_id', models.IntegerField()),
                ('작성자', models.CharField(max_length=255)),
                ('작성일', models.DateTimeField()),
                ('내용', models.CharField(max_length=255)),
            ],
        ),
    ]
