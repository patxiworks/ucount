# Generated by Django 5.0.3 on 2024-09-27 23:08

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='E1People',
            fields=[
                ('personid', models.AutoField(db_column='PersonID', primary_key=True, serialize=False)),
                ('surname', models.CharField(db_column='Surname', max_length=30)),
                ('firstname', models.CharField(db_column='FirstName', max_length=30, verbose_name='First name')),
                ('othername', models.CharField(blank=True, db_column='OtherName', max_length=30, null=True, verbose_name='Other name(s)')),
                ('dofb', models.DateField(blank=True, db_column='DofB', null=True, verbose_name='Date of birth')),
                ('phone', models.CharField(blank=True, db_column='Phone', max_length=20, null=True, verbose_name='Phone number')),
                ('email', models.EmailField(blank=True, db_column='Email', max_length=150, null=True, validators=[django.core.validators.EmailValidator()], verbose_name='Email address')),
                ('status', models.IntegerField(db_column='Status', default=1, editable=False)),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'Persons',
                'db_table': 'e1_people',
                'ordering': ('surname',),
            },
        ),
        migrations.CreateModel(
            name='E2ActivityType',
            fields=[
                ('activitytypeid', models.AutoField(db_column='ActivityTypeID', primary_key=True, serialize=False)),
                ('activitytype', models.CharField(db_column='ActivityType', max_length=15, verbose_name='Type of activity')),
                ('activitytypename', models.CharField(db_column='ActivityTypeName', max_length=100, verbose_name='Name of activity')),
                ('activityformat', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], db_column='ActivityFormat', default='open', max_length=10, verbose_name='Activity format')),
                ('serialnoonreport', models.IntegerField(blank=True, db_column='SerialNoOnReport', default=1, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'Activity Type',
                'verbose_name_plural': 'Activity Types',
                'db_table': 'e2_activity_type',
            },
        ),
        migrations.CreateModel(
            name='E3Categories',
            fields=[
                ('categoryid', models.AutoField(db_column='CategoryID', primary_key=True, serialize=False)),
                ('category', models.CharField(db_column='Category', max_length=6)),
                ('description', models.CharField(blank=True, db_column='CategoryDescription', max_length=50)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'e3_categories',
            },
        ),
        migrations.CreateModel(
            name='E5Centres',
            fields=[
                ('centreid', models.AutoField(db_column='CentreID', primary_key=True, serialize=False)),
                ('centre', models.CharField(db_column='Centre', default='', max_length=50, verbose_name='Name of centre')),
                ('acronym', models.CharField(db_column='CentreAcronym', default='', max_length=50, verbose_name='Acronym')),
            ],
            options={
                'verbose_name': 'Centre',
                'verbose_name_plural': 'Centres',
                'db_table': 'e5_centres',
            },
        ),
        migrations.CreateModel(
            name='E6Cities',
            fields=[
                ('cityid', models.AutoField(db_column='CityID', primary_key=True, serialize=False)),
                ('city', models.CharField(db_column='City', default='', max_length=20, verbose_name='City')),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='E4Groups',
            fields=[
                ('groupid', models.AutoField(db_column='GroupID', primary_key=True, serialize=False)),
                ('group', models.CharField(db_column='Group', max_length=50)),
                ('centre', models.ForeignKey(blank=True, db_column='Centre', default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e5centres', verbose_name='Centre')),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
                'db_table': 'e4_groups',
            },
        ),
        migrations.CreateModel(
            name='E2Activities',
            fields=[
                ('activityid', models.AutoField(db_column='ActivityID', primary_key=True, serialize=False)),
                ('activity', models.CharField(db_column='ActivityName', default='', max_length=50, verbose_name='Name of activity')),
                ('description', models.TextField(blank=True, db_column='ActivityDescription', default='', null=True, verbose_name='Description')),
                ('format', models.CharField(db_column='Format', default='1', editable=False, max_length=10)),
                ('person', models.ForeignKey(blank=True, db_column='PersonID', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e1people', verbose_name='Person in charge')),
                ('activitytype', models.ForeignKey(db_column='ActivityTypeID', default=0, on_delete=django.db.models.deletion.CASCADE, to='backend.e2activitytype', verbose_name='Type of activity')),
                ('centre', models.ForeignKey(blank=True, db_column='Centre', default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e5centres', verbose_name='Centre')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
                'db_table': 'e2_activities',
            },
        ),
        migrations.AddField(
            model_name='e1people',
            name='centre',
            field=models.ForeignKey(blank=True, db_column='Centre', default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.e5centres', verbose_name='Centre'),
        ),
        migrations.AddField(
            model_name='e5centres',
            name='city',
            field=models.ForeignKey(db_column='City', default='', on_delete=django.db.models.deletion.CASCADE, to='backend.e6cities', verbose_name='City'),
        ),
        migrations.CreateModel(
            name='R1ActivitiesLog',
            fields=[
                ('activitieslogid', models.AutoField(db_column='ActivitiesLogID', primary_key=True, serialize=False)),
                ('activitydate', models.DateField(db_column='ActivityDate', verbose_name='Date')),
                ('activityenddate', models.DateField(blank=True, db_column='ActivityEndDate', null=True, verbose_name='End Date')),
                ('activity', models.ForeignKey(db_column='ActivityID', on_delete=django.db.models.deletion.CASCADE, to='backend.e2activities', verbose_name='Activity')),
            ],
            options={
                'verbose_name': 'Event (Open)',
                'verbose_name_plural': 'Events (Open)',
                'db_table': 'r1_activities_log',
            },
        ),
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
        migrations.CreateModel(
            name='R4GroupAssign',
            fields=[
                ('groupassignid', models.AutoField(db_column='GroupAssignID', primary_key=True, serialize=False)),
                ('group', models.ForeignKey(db_column='GroupID', on_delete=django.db.models.deletion.CASCADE, to='backend.e4groups')),
                ('person', models.ForeignKey(db_column='PersonID', default=1, on_delete=django.db.models.deletion.CASCADE, to='backend.e1people')),
            ],
            options={
                'verbose_name': 'Group',
                'db_table': 'r4_group_assign',
            },
        ),
        migrations.CreateModel(
            name='R5AttendedByAssign',
            fields=[
                ('attendedbyassignid', models.AutoField(db_column='AttendedByAssignID', primary_key=True, serialize=False)),
                ('attendedby', models.ForeignKey(db_column='AttendedBy', on_delete=django.db.models.deletion.CASCADE, related_name='attendedby', to='backend.e1people')),
                ('person', models.ForeignKey(db_column='Person', on_delete=django.db.models.deletion.CASCADE, related_name='person', to='backend.e1people')),
            ],
            options={
                'verbose_name': 'Attended by',
                'verbose_name_plural': 'Attended by',
                'db_table': 'r5_attendedby_assign',
            },
        ),
        migrations.CreateModel(
            name='R6ActivityAssign',
            fields=[
                ('activityassignid', models.AutoField(db_column='ActivityAssignID', primary_key=True, serialize=False)),
                ('activity', models.ForeignKey(db_column='ActivityID', on_delete=django.db.models.deletion.CASCADE, to='backend.e2activities')),
                ('member', models.ForeignKey(blank=True, db_column='PersonID', on_delete=django.db.models.deletion.CASCADE, to='backend.e1people')),
            ],
            options={
                'verbose_name': 'Member',
                'verbose_name_plural': 'Members',
                'db_table': 'r6_activity_assign',
            },
        ),
        migrations.CreateModel(
            name='R2Participants',
            fields=[
                ('participantsid', models.AutoField(db_column='ParticipantsID', primary_key=True, serialize=False)),
                ('activitieslogid', models.ForeignKey(db_column='ActivitiesLogID', default=0, on_delete=django.db.models.deletion.CASCADE, to='backend.r1activitieslog', verbose_name='Activity')),
                ('person', models.ForeignKey(db_column='PersonID', on_delete=django.db.models.deletion.CASCADE, to='backend.e1people', verbose_name='Person')),
            ],
            options={
                'verbose_name': 'Participant',
                'verbose_name_plural': 'Participants',
                'db_table': 'r2_participants',
                'unique_together': {('activitieslogid', 'person')},
            },
        ),
        migrations.CreateModel(
            name='R3CategoryAssign',
            fields=[
                ('categoryassignid', models.AutoField(db_column='CategoryAssignID', primary_key=True, serialize=False)),
                ('startdate', models.DateField(db_column='StartDate', verbose_name='Start date')),
                ('enddate', models.DateField(blank=True, db_column='EndDate', editable=False, null=True)),
                ('category', models.ForeignKey(db_column='CategoryID', default=1, on_delete=django.db.models.deletion.CASCADE, to='backend.e3categories')),
                ('person', models.ForeignKey(db_column='PersonID', default=1, on_delete=django.db.models.deletion.CASCADE, to='backend.e1people')),
            ],
            options={
                'verbose_name': 'category (status)',
                'verbose_name_plural': 'Categories (Status)',
                'db_table': 'r3_category_assign',
                'unique_together': {('person', 'category')},
            },
        ),
    ]
