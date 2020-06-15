# Generated by Django 2.2.13 on 2020-06-15 08:50

from django.db import migrations


def update_destinations_code(apps, schema_editor):
    Aid = apps.get_model('aids', 'Aid')
    aids = Aid.objects.filter(destinations__overlap=['service', 'works'])
    for aid in aids:
        aid.destinations.append('investment')

        if 'service' in aid.destinations:
            aid.destinations.remove('service')

        if 'works' in aid.destinations:
            aid.destinations.remove('works')
        aid.save()


class Migration(migrations.Migration):

    dependencies = [
        ('aids', '0106_auto_20200612_1210'),
    ]

    operations = [
        migrations.RunPython(update_destinations_code),
    ]
