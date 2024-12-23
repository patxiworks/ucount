# Generated by Django 5.0.3 on 2024-11-18 10:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_activitysummary_participantsummary_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='r2organisers',
            unique_together={('activity', 'person')},
        ),
        migrations.AddField(
            model_name='r2organisers',
            name='activity',
            field=models.ForeignKey(db_column='ActivityID', default=0, on_delete=django.db.models.deletion.CASCADE, to='backend.e2activities', verbose_name='Activity'),
        ),
        migrations.AlterField(
            model_name='e1people',
            name='surname',
            field=models.CharField(db_column='Surname', max_length=30, verbose_name='Surname'),
        ),
        migrations.AlterField(
            model_name='userstatus',
            name='level',
            field=models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3)], db_column='Level', default=0),
        ),
        migrations.RemoveField(
            model_name='r2organisers',
            name='activitieslogid',
        ),
    ]