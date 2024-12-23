from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User
from django.utils.timezone import now
from rest_framework import serializers
from backend.models import *
import time


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

        
class PeopleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = E1People
        fields = ['personid', 'surname','firstname', 'othername']
        

class CatAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = R3CategoryAssign
        fields = ['person_id','person__surname','person__firstname','person__othername']


class ParticipantsSerializer(serializers.ModelSerializer):
    #activitieslogid = serializers.PrimaryKeyRelatedField(queryset=R1ActivitiesLog.objects.all())
    #person = serializers.PrimaryKeyRelatedField(queryset=E1People.objects.all())

    class Meta:
        model = R2Participants
        fields = ['participantsid', 'activitieslogid', 'person', 'entrydate', 'entryuser', 'placeholder']


class UserPlaceholdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlaceholders
        fields = ['surname', 'firstname', 'othername', 'tempid']

    def validate(self, data):
        # Handle the case where "othername" might be undefined
        #if 'tempid' not in data or data['tempid'] == 'undefined':
        #    data['tempid'] = round(time.time())
        if 'othername' in data and data['othername'] == 'undefined':
            data['othername'] = ""
        return data


class E2ActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = E2Activities
        fields = ['activityid', 'activity', 'description', 'person']
        

class E2ActivityTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()

    class Meta:
        model = E2ActivityType
        fields = ['activitytypeid', 'activitytype', 'activitytypename', 'activityformat', 'activities']

    def get_activities(self, obj):
        # Get the activities related to this activity type
        activities = self.context.get('activities_by_type', {}).get(obj.activitytypeid, [])
        return E2ActivitiesSerializer(activities, many=True).data


class R1ActivitiesLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = R1ActivitiesLog
        fields = ['activitieslogid', 'activity', 'activitydate', 'activityenddate']


class E1PeopleSerializer(serializers.ModelSerializer):
    invitedby = serializers.IntegerField(write_only=True, required=False)
    #eventid = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = E1People
        fields = fields = [
            'personid', 'surname', 'firstname', 'othername',
            'phone', 'email', 'centre', 'invitedby',
        ]

    def validate_email(self, value):
        if E1People.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    '''
    def create(self, validated_data):
        print(validated_data)
        # Extract additional fields
        friend_id = validated_data.pop('invitedby', None)
        eventid = validated_data.pop('eventid')

        # Create the person record
        person = E1People.objects.create(**validated_data)

        # Create R5AttendedByAssign record if a friend ID is provided
        if friend_id:
            R5AttendedByAssign.objects.create(person=person, attendedby_id=friend_id)

        # Create R2Participants record
        R2Participants.objects.create(
            activitieslogid_id=eventid,  # Reference to R1ActivitiesLog
            person=person,
            entrydate=now(),
            entryuser=None,
            placeholder=None
        )
        return person
    '''
    def create(self, validated_data):
        print(validated_data)
        # Extract additional fields
        friend_id = validated_data.pop('invitedby', None)
        #eventid = validated_data.pop('eventid')

        try:
            # Step 1: Create the person record
            try:
                person = E1People.objects.create(**validated_data)
            except IntegrityError as e:
                raise ValidationError({"person": f"Error creating person: {str(e)}"})

            # Step 2: Create R5AttendedByAssign record if a friend ID is provided
            if friend_id:
                try:
                    R5AttendedByAssign.objects.create(person=person, attendedby_id=friend_id)
                except IntegrityError as e:
                    raise ValidationError({"friend": f"Error creating person: {str(e)}"})

        except ValidationError as ve:
            # Catch and re-raise validation errors
            raise ve
        except Exception as e:
            # Catch any other unexpected errors
            raise ValidationError({"error": f"An unexpected error occurred: {str(e)}"})

        # Return the created person record
        return person
    

class E5CentresSerializer(serializers.ModelSerializer):
    class Meta:
        model = E5Centres
        fields = ['centreid', 'centre']  # Only include fields necessary for the dropdown
    
