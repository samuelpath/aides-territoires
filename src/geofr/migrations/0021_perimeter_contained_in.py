# Generated by Django 2.2.1 on 2019-09-19 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geofr', '0020_update_mainland_overseas_perimeters_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='perimeter',
            name='contained_in',
            field=models.ManyToManyField(blank=True, to='geofr.Perimeter', verbose_name='Contained in'),
        ),
    ]