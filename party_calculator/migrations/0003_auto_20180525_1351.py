# Generated by Django 2.0.5 on 2018-05-25 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party_calculator', '0002_auto_20180525_1326'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partydesiredfood',
            old_name='food_id',
            new_name='food',
        ),
        migrations.RenameField(
            model_name='partydesiredfood',
            old_name='party_id',
            new_name='party',
        ),
    ]
