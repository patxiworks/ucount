# Generated by Django 5.0.3 on 2024-09-16 11:00

from django.db import migrations, models

CREATE_SQL = """
CREATE VIEW activity_summary AS
SELECT
--strftime('%Y-%m', ActivityDate) AS YrMonth,
row_number() OVER () as SummaryID,
ActivityDate,
ActivityName,
C1.CentreAcronym AS ActivityCentre,
ActivityType,
ActivityTypeName,
--SerialNoOnReport,
Surname ||', '|| FirstName AS ParticipantName,
Category as ParticipantCategory,
C2.CentreAcronym AS ParticipantCentre,
--r4_group_assign.GroupID,
`Group` as ParticipantGroup
--COUNT (Category) as Total 
FROM r2_participants
JOIN r3_category_assign on r2_participants.PersonID = r3_category_assign.PersonID
JOIN r1_activities_log ON r2_participants.ActivitiesLogID = r1_activities_log.ActivitiesLogID
JOIN e2_activities ON r1_activities_log.ActivityID = e2_activities.ActivityID
JOIN e2_activity_type ON e2_activities.ActivityTypeID = e2_activity_type.ActivityTypeID
JOIN r4_group_assign ON r2_participants.PersonID = r4_group_assign.PersonID
JOIN e4_groups ON r4_group_assign.GroupID = e4_groups.GroupID
JOIN e3_categories ON r3_category_assign.CategoryID = e3_categories.CategoryID
JOIN e1_people ON r2_participants.PersonID = e1_people.PersonID
JOIN e5_centres C1 ON e2_activities.Centre = C1.CentreID
JOIN e5_centres C2 ON e1_people.Centre = C2.CentreID
--GROUP BY GroupID, Category, e2_activity_type.ActivityTypeID
ORDER BY ActivityDate ASC;
"""
DROP_SQL = "DROP VIEW IF EXISTS activity_summary;"


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0022_merge_20240916_1049'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_SQL,
            reverse_sql=DROP_SQL,
        ),
    ]
