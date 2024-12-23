# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from datetime import datetime
from django.utils import timezone

from django.db import models
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint

EVENT_CHOICES = (
    ("open", "Open"),
    ("closed", "Closed")
)
EVENT_DEFAULT = "open"
USER_LEVELS = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
)


class E6Cities(models.Model):
    cityid = models.AutoField(db_column='CityID', primary_key=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=20, default='', verbose_name='City')  # Field name made lowercase.

    class Meta:
        #managed = False
        #db_table = 'e6_city'
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.city
    

class E5Centres(models.Model):
    centreid = models.AutoField(db_column='CentreID', primary_key=True)  # Field name made lowercase.
    centre = models.CharField(db_column='Centre', default='', max_length=50, verbose_name='Name of centre')  # Field name made lowercase.
    acronym = models.CharField(db_column='CentreAcronym', default='', max_length=50, verbose_name='Acronym')
    #external = models.CharField(db_column='CentreExternal', default='', max_length=50, verbose_name='External name', blank=True, null=True)
    city = models.ForeignKey(E6Cities, models.CASCADE, db_column='City', default='', verbose_name='City')

    class Meta:
        #managed = False
        db_table = 'e5_centres'
        verbose_name = "Centre"
        verbose_name_plural = "Centres"

    def __str__(self):
        return self.centre


'''class ExtendedUser(AbstractUser):
    centre = models.ForeignKey(E5Centres, models.CASCADE, db_column='Centre', verbose_name='Centre', default='', blank=True, null=True)
'''

class E1People(models.Model):
    personid = models.AutoField(db_column='PersonID', primary_key=True)  
    surname = models.CharField(db_column='Surname', max_length=30, verbose_name='Surname')  
    firstname = models.CharField(db_column='FirstName', max_length=30, verbose_name='First name')  
    othername = models.CharField(db_column='OtherName', max_length=30, default='', blank=True, null=True, verbose_name='Other name(s)')  
    dofb = models.DateField(db_column='DofB', blank=True, null=True, verbose_name='Date of birth')  
    phone = models.CharField(db_column='Phone', max_length=20, blank=True, null=True, verbose_name='Phone number')  
    email = models.EmailField(db_column='Email', max_length=150, verbose_name='Email address', validators=[validate_email])  
    centre = models.ForeignKey(E5Centres, models.CASCADE, db_column='Centre', verbose_name='Centre', default='', blank=True, null=True)
    status = models.IntegerField(db_column='Status', default=1, editable=False)

    class Meta:
        #managed = False
        db_table = 'e1_people'
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        ordering = ('surname',)
        constraints = [
            UniqueConstraint(fields=['surname', 'firstname', 'othername'],
                             name='unique_names'),
            UniqueConstraint(fields=['email'],
                             name='unique_email'),
        ]

    def __str__(self):
        return self.surname + ' ' + self.firstname
    

class E2ActivityType(models.Model):
    activitytypeid = models.AutoField(db_column='ActivityTypeID', primary_key=True)  # Field name made lowercase.
    activitytype = models.CharField(db_column='ActivityType', max_length=15, verbose_name='Type of activity')  # Field name made lowercase.
    activitytypename = models.CharField(db_column='ActivityTypeName', max_length=100, verbose_name='Name of activity')  # Field name made lowercase.
    activityformat = models.CharField(db_column='ActivityFormat', max_length=10, verbose_name='Activity format', choices=EVENT_CHOICES, default=EVENT_DEFAULT)
    serialnoonreport = models.IntegerField(db_column='SerialNoOnReport', editable=False, default=1, blank=True, null=True)  # This field is marked for deletion.

    class Meta:
        #managed = False
        db_table = 'e2_activity_type'
        verbose_name = "Activity Type"
        verbose_name_plural = "Activity Types"

    def __str__(self):
        return self.activitytype


class E2Activities(models.Model):
    activityid = models.AutoField(db_column='ActivityID', primary_key=True)  # Field name made lowercase.
    activitytype = models.ForeignKey(E2ActivityType, models.CASCADE, db_column='ActivityTypeID', default=0, verbose_name='Type of activity')  # Field name made lowercase.
    centre = models.ForeignKey(E5Centres, models.CASCADE, db_column='Centre', verbose_name='Centre', default='', blank=True, null=True)
    activity = models.CharField(db_column='ActivityName', max_length=50, default='', verbose_name='Name of activity')
    description = models.TextField(db_column='ActivityDescription', default='', verbose_name='Description', blank=True, null=True)  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', blank=True, null=True, verbose_name='Person in charge')  # Field name made lowercase.
    format = models.CharField(db_column='Format', max_length=10, editable=False, default='1') # This field is marked for deletion

    class Meta:
        #managed = False
        db_table = 'e2_activities'
        verbose_name = "Activity"
        verbose_name_plural = "Activities"

    def __str__(self):
        return self.activity


class E3Categories(models.Model):
    categoryid = models.AutoField(db_column='CategoryID', primary_key=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=6)  # Field name made lowercase.
    description = models.CharField(db_column='CategoryDescription', max_length=50, blank=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'e3_categories'
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.description


class E4Groups(models.Model):
    groupid = models.AutoField(db_column='GroupID', primary_key=True)  # Field name made lowercase.
    group = models.CharField(db_column='Group', max_length=50)  # Field name made lowercase.
    centre = models.ForeignKey(E5Centres, models.CASCADE, db_column='Centre', verbose_name='Centre', default='', blank=True, null=True)
    #egr = models.ForeignKey(E1People, models.DO_NOTHING, db_column='egr', default=1, related_name='egr', verbose_name='Group head')  # Field name made lowercase.
    #cel1 = models.ForeignKey(E1People, models.DO_NOTHING, db_column='cel', default=1, related_name='cel', verbose_name='Group coordinator 1')  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'e4_groups'
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.centre.acronym + " - " + self.group


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(db_column='Level', choices=USER_LEVELS, default=0)
    centre = models.ForeignKey(E5Centres, models.CASCADE, db_column='Centre', blank=True, null=True)
    group = models.ForeignKey(E4Groups, models.CASCADE, db_column='Group', blank=True, null=True)

    class Meta:
        verbose_name = "User level and status"


class UserPerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    person = models.ForeignKey(E1People, models.CASCADE, db_column='Person', blank=True, null=True)

    class Meta:
        verbose_name = "User person"


class R1ActivitiesLog(models.Model):
    activitieslogid = models.AutoField(db_column='ActivitiesLogID', primary_key=True)  # Field name made lowercase.
    activity = models.ForeignKey(E2Activities, models.CASCADE, db_column='ActivityID', verbose_name='Activity')  # Field name made lowercase.
    activitydate = models.DateTimeField(db_column='ActivityDate', verbose_name='Date')  # Field name made lowercase.
    activityenddate = models.DateTimeField(db_column='ActivityEndDate', verbose_name='End Date', blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'r1_activities_log'
        verbose_name = "Event (Open)"
        verbose_name_plural = "Events (Open)"

    def __str__(self):
        return self.activity.activity


class MemberActivities(R1ActivitiesLog):
    class Meta:
        proxy = True
        verbose_name = "Event (Closed)"
        verbose_name_plural = "Events (Closed)"


class UserPlaceholders(models.Model):
    placeholderid = models.AutoField(db_column='PlaceholderID', primary_key=True)  # Field name made lowercase.
    tempid = models.IntegerField(db_column='TempID', blank=True, null=True )  # Field name made lowercase.
    surname = models.CharField(db_column='Surname', max_length=30, verbose_name='Surname' )
    firstname = models.CharField(db_column='FirstName', max_length=30, verbose_name='First name')
    othername = models.CharField(db_column='OtherName', max_length=30, blank=True, null=True, verbose_name='Other name(s)')
    
    class Meta:
        verbose_name = "User Placeholder"
        unique_together = (("surname", "firstname", "othername"))

    def __str__(self):
        return self.surname + ' ' + self.firstname


class R2Participants(models.Model):
    participantsid = models.AutoField(db_column='ParticipantsID', primary_key=True)  # Field name made lowercase.
    activitieslogid = models.ForeignKey(R1ActivitiesLog, models.CASCADE, db_column='ActivitiesLogID', default=0, verbose_name='Activity')  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', verbose_name='Person', blank=True, null=True)  # Field name made lowercase.
    placeholder = models.ForeignKey(UserPlaceholders, models.SET_NULL, db_column='PlaceholderID', blank=True, null=True)
    entrydate = models.DateTimeField(default=timezone.now, blank=True, db_column='EntryDate')
    entryuser = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='EnteredBy', verbose_name='Entered by', blank=True, null=True)

    class Meta:
        #managed = False
        db_table = 'r2_participants'
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
        #unique_together = (("activitieslogid", "person"))
        constraints = [
            UniqueConstraint(fields=['activitieslogid', 'person'],
                             condition=Q(placeholder=None),
                             name='unique_with_person'),
            UniqueConstraint(fields=['activitieslogid', 'placeholder'],
                             condition=Q(person=None),
                             name='unique_with_placeholder'),
        ]

    def __str__(self):
        if self.person:
            return self.person.surname + ' ' + self.person.firstname
        elif self.placeholder:
            return self.placeholder.surname + ' ' + self.placeholder.firstname
        else:
            return str(self.participantsid)


class R2Organisers(models.Model):
    organiserid = models.AutoField(db_column='OrganisersID', primary_key=True)  # Field name made lowercase.
    activity = models.ForeignKey(E2Activities, models.CASCADE, db_column='ActivityID', default=0, verbose_name='Activity')  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', verbose_name='Person')  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'r2_organisers'
        verbose_name = "Organiser"
        verbose_name_plural = "Organisers"
        #unique_together = (("activity", "person"))

    def __str__(self):
        return self.person.surname + ' ' + self.person.firstname


class R3CategoryAssign(models.Model):
    categoryassignid = models.AutoField(db_column='CategoryAssignID', primary_key=True)  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', default=1)  # Field name made lowercase.
    category = models.ForeignKey(E3Categories, models.CASCADE, db_column='CategoryID', default=1)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', verbose_name='Start date')  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True, editable=False)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'r3_category_assign'
        verbose_name = "category (status)"
        verbose_name_plural = "Categories (Status)"
        unique_together = (("person", "category"))

    def __str__(self):
        return self.category.description


class R4GroupAssign(models.Model):
    groupassignid = models.AutoField(db_column='GroupAssignID', primary_key=True)  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', default=1)  # Field name made lowercase.
    group = models.ForeignKey(E4Groups, models.CASCADE, db_column='GroupID')  # Field name made lowercase.
    #startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    #enddate = models.DateField(db_column='EndDate', blank=True, null=True, editable=False)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'r4_group_assign'
        verbose_name = "Group"

    def __str__(self):
        return self.group.group


class R5AttendedByAssign(models.Model):
    attendedbyassignid = models.AutoField(db_column='AttendedByAssignID', primary_key=True)  # Field name made lowercase.
    person = models.ForeignKey(E1People, models.CASCADE, db_column='Person', related_name='person')  # Field name made lowercase.
    attendedby = models.ForeignKey(E1People, models.CASCADE, db_column='AttendedBy', related_name='attendedby')  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'r5_attendedby_assign'
        verbose_name = "Attended by"
        verbose_name_plural = "Attended by"

    def __str__(self):
        return self.attendedby.surname + ' ' + self.attendedby.firstname


class R6ActivityAssign(models.Model):
    activityassignid = models.AutoField(db_column='ActivityAssignID', primary_key=True)  # Field name made lowercase.
    activity = models.ForeignKey(E2Activities, models.CASCADE, db_column='ActivityID')  # Field name made lowercase.
    #member = models.ManyToManyField(E1People, db_column='PersonID')  # Field name made lowercase.
    member = models.ForeignKey(E1People, models.CASCADE, db_column='PersonID', blank=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'r6_activity_assign'
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def __str__(self):
        return self.member.surname + ' ' + self.member.firstname


class ActivitySummary(models.Model):
    summaryid = models.AutoField(db_column='SummaryID', primary_key=True)
    eventid = models.IntegerField(db_column='EventID', blank=True, null=True) # represents ActivitiesLogID
    activitydate = models.DateField(db_column='ActivityDate', blank=True, null=True)  # Field name made lowercase.
    activityenddate = models.DateField(db_column='ActivityEndDate', blank=True, null=True)
    activityid = models.IntegerField(db_column='ActivityID', blank=True, null=True)
    activityname = models.CharField(db_column='ActivityName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    activitycentre = models.CharField(db_column='ActivityCentre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    activitytype = models.CharField(db_column='ActivityType', max_length=15, blank=True, null=True)  # Field name made lowercase.
    activitytypename = models.CharField(db_column='ActivityTypeName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    participantid = models.IntegerField(db_column='ParticipantID', blank=True, null=True)
    participanttype = models.TextField(db_column='ParticipantType', blank=True, null=True)
    participantname = models.TextField(db_column='ParticipantName', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    participantcategory = models.CharField(db_column='ParticipantCategory', max_length=6, blank=True, null=True)  # Field name made lowercase.
    participantcentre = models.CharField(db_column='ParticipantCentre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    participantgroup = models.CharField(db_column='ParticipantGroup', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'activity_summary'


class ParticipantSummary(models.Model):
    summaryid = models.AutoField(db_column='SummaryID', primary_key=True)
    participantid = models.IntegerField(db_column='ParticipantID', blank=True, null=True)
    participantname = models.TextField(db_column='ParticipantName', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    participantcategory = models.CharField(db_column='ParticipantCategory', max_length=6, blank=True, null=True)  # Field name made lowercase.
    participantcentre = models.CharField(db_column='ParticipantCentre', max_length=50, blank=True, null=True)  # Field name made lowercase.
    participantgroup = models.CharField(db_column='ParticipantGroup', max_length=50, blank=True, null=True)  # Field name made lowercase.
    participantfriendid = models.IntegerField(db_column='ParticipantFriendID', blank=True, null=True)
    participantfriendname = models.TextField(db_column='ParticipantFriendName', blank=True, null=True)
    #participantfriendcat = models.TextField(db_column='ParticipantFriendCategory', blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'participant_summary'

