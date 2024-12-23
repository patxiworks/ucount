# Generated by Django 5.0.3 on 2024-12-12 12:02

from django.db import migrations, models

CREATE_SQL_activity = """
DROP VIEW IF EXISTS activity_summary;
CREATE VIEW activity_summary AS
SELECT
    -- Summary ID
    row_number() OVER () AS SummaryID,
	--*,
    -- Activity Details
    r1_activities_log.ActivitiesLogID AS EventID,
    r1_activities_log.ActivityDate,
    r1_activities_log.ActivityEndDate,
    e2_activities.ActivityID,
    e2_activities.ActivityName,
    C1.CentreAcronym AS ActivityCentre,
    ActivityType,
    e2_activity_type.ActivityTypeName,

    -- Participant Details
    participants.EntityID AS ParticipantID,
	participants.SourceField AS ParticipantType,
    participants.Surname || ', ' || participants.FirstName AS ParticipantName,
    e3_categories.Category AS ParticipantCategory,
    C2.CentreAcronym AS ParticipantCentre,
    e4_groups.`Group` AS ParticipantGroup

FROM 
    -- Participant Subquery
    (
        SELECT
			-- Select the value from either Person or Placeholder
			CASE
				WHEN rp.personid IS NOT NULL THEN CAST(rp.personid AS VARCHAR)
				ELSE CAST(rp.placeholder AS VARCHAR)
			END AS EntityID,
			
			rp.ActivitiesLogID,
			rp.EntryDate,

			-- Indicate the source field
			CASE
				WHEN rp.personid IS NOT NULL THEN 'Person'
				ELSE 'Placeholder'
			END AS SourceField,

			-- Common name fields
			CASE
				WHEN rp.personid IS NOT NULL THEN ep.firstname
				ELSE up.firstname
			END AS FirstName,

			CASE
				WHEN rp.personid IS NOT NULL THEN ep.surname
				ELSE up.surname
			END AS Surname,

			CASE
				WHEN rp.personid IS NOT NULL THEN ep.othername
				ELSE up.othername
			END AS OtherName

		FROM R2_Participants rp
		LEFT JOIN E1_People ep
			ON rp.personid = ep.personid
		LEFT JOIN backend_userplaceholders up
			ON rp.placeholder = up.ParticipantsID
    ) AS participants

LEFT OUTER JOIN 
    -- Category Subquery
    (
        SELECT *, 
            RANK() OVER (PARTITION BY PersonID ORDER BY StartDate DESC) AS date_rank 
        FROM r3_category_assign
    ) AS categories
    ON participants.EntityID = categories.PersonID AND categories.date_rank = 1

JOIN r1_activities_log ON participants.ActivitiesLogID = r1_activities_log.ActivitiesLogID
JOIN e2_activities ON r1_activities_log.ActivityID = e2_activities.ActivityID
JOIN e2_activity_type ON e2_activities.ActivityTypeID = e2_activity_type.ActivityTypeID
LEFT OUTER JOIN r4_group_assign ON participants.EntityID = r4_group_assign.PersonID
LEFT OUTER JOIN e4_groups ON r4_group_assign.GroupID = e4_groups.GroupID
LEFT OUTER JOIN e3_categories ON categories.CategoryID = e3_categories.CategoryID
LEFT OUTER JOIN e1_people ON participants.EntityID = e1_people.PersonID
LEFT OUTER JOIN e5_centres C1 ON e2_activities.Centre = C1.CentreID
LEFT OUTER JOIN e5_centres C2 ON e1_people.Centre = C2.CentreID

ORDER BY participants.EntryDate ASC;
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
        ('backend', '0039_activitysummary_participantsummary'),
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
