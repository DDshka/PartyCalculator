# Generated by Django 2.0.5 on 2018-06-18 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField(default=False)),
                ('total_sponsored', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderedFood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('quantity', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('state', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=512)),
                ('duration', models.DurationField(null=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemplateMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemplateOrderedFood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=16)),
                ('quantity', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemplateParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('duration', models.DurationField(null=True)),
                ('state', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive', max_length=512)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
