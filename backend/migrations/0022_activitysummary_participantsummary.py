# Generated by Django 5.0.3 on 2024-11-27 16:05

from django.db import migrations, models

CREATE_SQL_activity = """
DROP VIEW IF EXISTS activity_summary;
CREATE VIEW activity_summary AS
SELECT
--strftime('%Y-%m', ActivityDate) AS YrMonth,
row_number() OVER () as SummaryID,
r1_activities_log.ActivitiesLogID as EventID,
ActivityDate,
ActivityEndDate,
e2_activities.ActivityID,
ActivityName,
C1.CentreAcronym AS ActivityCentre,
ActivityType,
ActivityTypeName,
e1_people.PersonID as ParticipantID,
Surname ||', '|| FirstName AS ParticipantName,
Category as ParticipantCategory,
C2.CentreAcronym AS ParticipantCentre,
`Group` as ParticipantGroup
FROM r2_participants
JOIN 
	(SELECT *, 
		RANK() OVER (PARTITION BY PersonID ORDER BY StartDate DESC) date_rank 
		FROM r3_category_assign
	) AS categories
	ON r2_participants.PersonID = categories.PersonID AND categories.date_rank = 1
JOIN r1_activities_log ON r2_participants.ActivitiesLogID = r1_activities_log.ActivitiesLogID
JOIN e2_activities ON r1_activities_log.ActivityID = e2_activities.ActivityID
JOIN e2_activity_type ON e2_activities.ActivityTypeID = e2_activity_type.ActivityTypeID
LEFT OUTER JOIN r4_group_assign ON r2_participants.PersonID = r4_group_assign.PersonID
LEFT OUTER JOIN e4_groups ON r4_group_assign.GroupID = e4_groups.GroupID
JOIN e3_categories ON categories.CategoryID = e3_categories.CategoryID
JOIN e1_people ON r2_participants.PersonID = e1_people.PersonID
JOIN e5_centres C1 ON e2_activities.Centre = C1.CentreID
JOIN e5_centres C2 ON e1_people.Centre = C2.CentreID
ORDER BY ActivityDate ASC;
"""
DROP_SQL_activity = "DROP VIEW IF EXISTS activity_summary;"

CREATE_SQL_participant = """
DROP VIEW IF EXISTS participant_summary;
CREATE VIEW participant_summary AS
SELECT
row_number() OVER () as SummaryID,
P1.PersonID as ParticipantID,
P1.Surname ||', '|| P1.FirstName AS ParticipantName,
Category as ParticipantCategory,
CentreAcronym AS ParticipantCentre,
`Group` as ParticipantGroup,
AttendedBy as ParticipantFriendID,
P2.Surname ||', '|| P2.FirstName AS ParticipantFriendName
FROM e1_people P1
JOIN
	(SELECT *, 
		RANK() OVER (PARTITION BY PersonID ORDER BY StartDate DESC) date_rank 
		FROM r3_category_assign
	) AS categories
	ON P1.PersonID = categories.PersonID AND categories.date_rank = 1
LEFT OUTER JOIN r4_group_assign ON P1.PersonID = r4_group_assign.PersonID
LEFT OUTER JOIN e4_groups ON r4_group_assign.GroupID = e4_groups.GroupID
JOIN e3_categories ON categories.CategoryID = e3_categories.CategoryID
LEFT OUTER JOIN r5_attendedby_assign ON P1.PersonID = r5_attendedby_assign.Person
LEFT OUTER JOIN e1_people P2 ON r5_attendedby_assign.AttendedBy = P2.PersonID
JOIN e5_centres ON P1.Centre = e5_centres.CentreID
GROUP BY ParticipantID
ORDER BY ParticipantID ASC;
"""
DROP_SQL_participant = "DROP VIEW IF EXISTS participant_summary;"


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0021_alter_r2participants_unique_together_and_more'),
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
    ]
