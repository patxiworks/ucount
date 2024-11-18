from django.contrib.auth.models import Group, User
from rest_framework import serializers
from backend.models import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

        
class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = E1People
        fields = ['surname','firstname']

class CatAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = R3CategoryAssign
        fields = ['person_id','person__surname','person__firstname','person__othername']


class ParticipantsSerializer(serializers.ModelSerializer):
    activitieslogid = serializers.PrimaryKeyRelatedField(queryset=R1ActivitiesLog.objects.all())
    person = serializers.PrimaryKeyRelatedField(queryset=E1People.objects.all())

    class Meta:
        model = R2Participants
        fields = ['participantsid', 'activitieslogid', 'person']
