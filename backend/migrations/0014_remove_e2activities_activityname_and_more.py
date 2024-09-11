# Generated by Django 5.0.3 on 2024-08-30 12:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_remove_e2activities_activity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='e2activities',
            name='activityname',
        ),
        migrations.AddField(
            model_name='e2activities',
            name='activity',
            field=models.CharField(db_column='ActivityName', default='', max_length=50, verbose_name='Name of activity'),
        ),
        migrations.AddField(
            model_name='e2activities',
            name='centre',
            field=models.ForeignKey(blank=True, db_column='Centre', default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e5centres', verbose_name='Centre'),
        ),
        migrations.AlterField(
            model_name='e2activities',
            name='activitytype',
            field=models.ForeignKey(db_column='ActivityTypeID', default=0, on_delete=django.db.models.deletion.CASCADE, to='backend.e2activitytype', verbose_name='Type of activity'),
        ),
        migrations.AlterField(
            model_name='e2activities',
            name='person',
            field=models.ForeignKey(blank=True, db_column='PersonID', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e1people', verbose_name='Person in charge'),
        ),
        migrations.AlterField(
            model_name='r1activitieslog',
            name='activity',
            field=models.ForeignKey(db_column='ActivityID', on_delete=django.db.models.deletion.CASCADE, to='backend.e2activities', verbose_name='Activity'),
        ),
    ]
