# Generated by Django 2.2.7 on 2019-11-15 13:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0006_bookmark_alert_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='latest_alert_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Latest alert date'),
        ),
    ]
