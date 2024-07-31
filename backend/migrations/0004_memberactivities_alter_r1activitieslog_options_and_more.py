# Generated by Django 5.0.3 on 2024-05-13 11:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_remove_r2participants_person2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberActivities',
            fields=[
            ],
            options={
                'verbose_name': 'Event (Closed)',
                'verbose_name_plural': 'Events (Closed)',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('backend.r1activitieslog',),
        ),
        migrations.AlterModelOptions(
            name='r1activitieslog',
            options={'verbose_name': 'Event (Open)', 'verbose_name_plural': 'Events (Open)'},
        ),
        migrations.AddField(
            model_name='e2activitytype',
            name='activityformat',
            field=models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], db_column='ActivityFormat', default='open', max_length=10),
        ),
        migrations.AlterField(
            model_name='r6activityassign',
            name='member',
            field=models.ForeignKey(blank=True, db_column='PersonID', on_delete=django.db.models.deletion.DO_NOTHING, to='backend.e1people'),
        ),
    ]
