# Generated by Django 2.0.5 on 2018-06-04 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('party_calculator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='authModule.Profile'),
        ),
        migrations.AlterField(
            model_name='party',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='creator', to='authModule.Profile'),
        ),
    ]