# Generated by Django 5.1.7 on 2025-04-08 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_coachprofile_position_within_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='athleteprofile',
            name='name',
            field=models.CharField(default='Unknown', help_text='Name of athlete', max_length=255),
        ),
        migrations.AddField(
            model_name='coachprofile',
            name='name',
            field=models.CharField(default='Unknown', help_text='Name of athlete', max_length=255),
        ),
    ]
