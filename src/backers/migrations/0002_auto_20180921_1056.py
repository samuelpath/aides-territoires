# Generated by Django 2.1.1 on 2018-09-21 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backer',
            name='name',
            field=models.CharField(db_index=True, max_length=256, verbose_name='Name'),
        ),
    ]
