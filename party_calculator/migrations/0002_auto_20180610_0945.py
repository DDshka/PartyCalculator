# Generated by Django 2.0.5 on 2018-06-10 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('party_calculator_auth', '0001_initial'),
        ('party_calculator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='creator', to='party_calculator_auth.Profile'),
        ),
        migrations.AddField(
            model_name='party',
            name='members',
            field=models.ManyToManyField(related_name='memberships', through='party_calculator.Membership', to='party_calculator_auth.Profile'),
        ),
        migrations.AddField(
            model_name='party',
            name='ordered_food',
            field=models.ManyToManyField(related_name='ordered_by', to='party_calculator.OrderedFood'),
        ),
        migrations.AddField(
            model_name='orderedfood',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='party_calculator.Party'),
        ),
        migrations.AddField(
            model_name='membership',
            name='excluded_food',
            field=models.ManyToManyField(to='party_calculator.OrderedFood'),
        ),
        migrations.AddField(
            model_name='membership',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='party_calculator.Party'),
        ),
        migrations.AddField(
            model_name='membership',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='party_calculator_auth.Profile'),
        ),
    ]
