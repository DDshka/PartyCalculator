# Generated by Django 2.0.5 on 2018-05-31 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authModule', '0002_auto_20180531_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=128, null=True),
        ),
    ]
