from django.contrib.auth.models import Group, User
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
        fields = ['activityid', 'activity', 'person']
        

class E2ActivityTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()

    class Meta:
        model = E2ActivityType
        fields = ['activitytypeid', 'activitytype', 'activitytypename', 'activityformat', 'activities']

    def get_activities(self, obj):
        # Get the activities related to this activity type
        activities = self.context.get('activities_by_type', {}).get(obj.activitytypeid, [])
        return E2ActivitiesSerializer(activities, many=True).data


class E1PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = E1People
        fields = '__all__'

    def validate_email(self, value):
        if E1People.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class E5CentresSerializer(serializers.ModelSerializer):
    class Meta:
        model = E5Centres
        fields = ['centreid', 'centre']  # Only include fields necessary for the dropdown
    
