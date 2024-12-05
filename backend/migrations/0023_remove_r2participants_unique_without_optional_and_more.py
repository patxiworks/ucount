# Generated by Django 5.0.3 on 2024-11-27 16:54

from django.conf import settings
from django.db import migrations, models

CREATE_SQL_activity = """
DROP VIEW IF EXISTS activity_summary;
"""
DROP_SQL_activity = "DROP VIEW IF EXISTS activity_summary;"

CREATE_SQL_participant = """
DROP VIEW IF EXISTS participant_summary;

"""
DROP_SQL_participant = "DROP VIEW IF EXISTS participant_summary;"


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0022_activitysummary_participantsummary'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_SQL_activity,
            reverse_sql=DROP_SQL_activity,
        ),
        migrations.RunSQL(
            sql=CREATE_SQL_participant,
            reverse_sql=DROP_SQL_participant,
        ),
        migrations.RemoveConstraint(
            model_name='r2participants',
            name='unique_without_optional',
        ),
        migrations.AddConstraint(
            model_name='r2participants',
            constraint=models.UniqueConstraint(condition=models.Q(('person', None)), fields=('activitieslogid', 'placeholder'), name='unique_without_optional'),
        ),
    ]
