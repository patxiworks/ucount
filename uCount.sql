BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "e1_people" (
	"PersonID"	integer NOT NULL,
	"Surname"	varchar(30) NOT NULL,
	"FirstName"	varchar(30) NOT NULL,
	"OtherName"	varchar(30),
	"DofB"	date,
	"Phone"	varchar(20),
	"Email"	varchar(150),
	"Status"	integer NOT NULL,
	PRIMARY KEY("PersonID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "e2_activity_type" (
	"ActivityTypeID"	integer NOT NULL,
	"ActivityType"	varchar(15) NOT NULL,
	"ActivityTypeName"	varchar(100) NOT NULL,
	"SerialNoOnReport"	integer NOT NULL,
	PRIMARY KEY("ActivityTypeID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "e3_categories" (
	"CategoryID"	integer NOT NULL,
	"Category"	varchar(6) NOT NULL,
	"CategoryDescription"	varchar(50) NOT NULL,
	PRIMARY KEY("CategoryID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "e4_groups" (
	"GroupID"	integer NOT NULL,
	"Group"	varchar(50) NOT NULL,
	"cel"	integer NOT NULL,
	"egr"	integer NOT NULL,
	FOREIGN KEY("egr") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("cel") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("GroupID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r1_activities_log" (
	"ActivitiesLogID"	integer NOT NULL,
	"ActivityDate"	date NOT NULL,
	"ActivityID"	integer NOT NULL,
	FOREIGN KEY("ActivityID") REFERENCES "e2_activities"("ActivityID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("ActivitiesLogID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r4_group_assign" (
	"GroupAssignID"	integer NOT NULL,
	"GroupID"	integer NOT NULL,
	"PersonID"	integer NOT NULL,
	FOREIGN KEY("GroupID") REFERENCES "e4_groups"("GroupID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("PersonID") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("GroupAssignID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r5_attendedby_assign" (
	"AttendedByAssignID"	integer NOT NULL,
	"AttendedBy"	integer NOT NULL,
	"Person"	integer NOT NULL,
	FOREIGN KEY("AttendedBy") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("Person") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("AttendedByAssignID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r2_participants" (
	"ParticipantsID"	integer NOT NULL,
	"ActivitiesLogID"	integer NOT NULL,
	"PersonID"	integer NOT NULL,
	FOREIGN KEY("ActivitiesLogID") REFERENCES "r1_activities_log"("ActivitiesLogID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("PersonID") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("ParticipantsID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r3_category_assign" (
	"CategoryAssignID"	integer NOT NULL,
	"StartDate"	date NOT NULL,
	"EndDate"	date,
	"CategoryID"	integer NOT NULL,
	"PersonID"	integer NOT NULL,
	FOREIGN KEY("CategoryID") REFERENCES "e3_categories"("CategoryID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("PersonID") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("CategoryAssignID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "e2_activities" (
	"ActivityID"	integer NOT NULL,
	"ActivityDescription"	text NOT NULL,
	"ActivityTypeID"	integer NOT NULL,
	"Format"	varchar(10) NOT NULL,
	"PersonID"	integer,
	FOREIGN KEY("ActivityTypeID") REFERENCES "e2_activity_type"("ActivityTypeID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("PersonID") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("ActivityID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "r6_activity_assign" (
	"ActivityAssignID"	integer NOT NULL,
	"ActivityID"	integer NOT NULL,
	"PersonID"	integer NOT NULL,
	FOREIGN KEY("ActivityID") REFERENCES "e2_activities"("ActivityID") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("PersonID") REFERENCES "e1_people"("PersonID") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY("ActivityAssignID" AUTOINCREMENT)
);
INSERT INTO "e1_people" VALUES (1,'Ekwem','Kingsley',NULL,NULL,NULL,NULL,1);
INSERT INTO "e2_activity_type" VALUES (1,'circle','Circle of cooperators',1);
INSERT INTO "e3_categories" VALUES (1,'s','Supernumerary');
INSERT INTO "r3_category_assign" VALUES (1,'2024-03-25',NULL,1,1);
INSERT INTO "e2_activities" VALUES (1,'Lasode circle',1,'closed',1);
CREATE INDEX IF NOT EXISTS "e4_groups_cel_ea58b26e" ON "e4_groups" (
	"cel"
);
CREATE INDEX IF NOT EXISTS "e4_groups_egr_570ab159" ON "e4_groups" (
	"egr"
);
CREATE INDEX IF NOT EXISTS "r1_activities_log_ActivityID_23d4bf0a" ON "r1_activities_log" (
	"ActivityID"
);
CREATE INDEX IF NOT EXISTS "r4_group_assign_GroupID_6537ce2d" ON "r4_group_assign" (
	"GroupID"
);
CREATE INDEX IF NOT EXISTS "r4_group_assign_PersonID_175df9ae" ON "r4_group_assign" (
	"PersonID"
);
CREATE INDEX IF NOT EXISTS "r5_attendedby_assign_AttendedBy_beff7bb6" ON "r5_attendedby_assign" (
	"AttendedBy"
);
CREATE INDEX IF NOT EXISTS "r5_attendedby_assign_Person_e3e16dac" ON "r5_attendedby_assign" (
	"Person"
);
CREATE UNIQUE INDEX IF NOT EXISTS "r2_participants_ActivitiesLogID_PersonID_3ce49aa3_uniq" ON "r2_participants" (
	"ActivitiesLogID",
	"PersonID"
);
CREATE INDEX IF NOT EXISTS "r2_participants_ActivitiesLogID_15c8690d" ON "r2_participants" (
	"ActivitiesLogID"
);
CREATE INDEX IF NOT EXISTS "r2_participants_PersonID_73f0aa49" ON "r2_participants" (
	"PersonID"
);
CREATE UNIQUE INDEX IF NOT EXISTS "r3_category_assign_PersonID_CategoryID_851d1cb3_uniq" ON "r3_category_assign" (
	"PersonID",
	"CategoryID"
);
CREATE INDEX IF NOT EXISTS "r3_category_assign_CategoryID_8457c284" ON "r3_category_assign" (
	"CategoryID"
);
CREATE INDEX IF NOT EXISTS "r3_category_assign_PersonID_59e1a608" ON "r3_category_assign" (
	"PersonID"
);
CREATE INDEX IF NOT EXISTS "e2_activities_ActivityTypeID_679e33da" ON "e2_activities" (
	"ActivityTypeID"
);
CREATE INDEX IF NOT EXISTS "e2_activities_PersonID_99b728e0" ON "e2_activities" (
	"PersonID"
);
CREATE INDEX IF NOT EXISTS "r6_activity_assign_ActivityID_b275a13b" ON "r6_activity_assign" (
	"ActivityID"
);
CREATE INDEX IF NOT EXISTS "r6_activity_assign_PersonID_da352c2c" ON "r6_activity_assign" (
	"PersonID"
);
COMMIT;
