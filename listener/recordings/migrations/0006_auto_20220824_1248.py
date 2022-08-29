# Generated by Django 3.2.15 on 2022-08-24 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recordings', '0005_auto_20220824_0151'),
    ]

    operations = [
        migrations.AddField(
            model_name='detection',
            name='detected_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='filepath',
            field=models.FilePathField(default='', path='/home/pi/birdnetlib-listener/recordings'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recording',
            name='is_compressed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='recording',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
