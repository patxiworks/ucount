from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db.models import Count, Q, F

from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, authentication, viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

from backend.models import *
from backend.api.serializers import *
from backend.context import check_valid_user

from datetime import date, datetime, timedelta
import json, os


class LoginView(KnoxLoginView):
    #authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


def get_json(request):
    from pathlib import Path
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent
    with open(os.path.join(BASE_DIR, 'static/backend/assets/eventDates.json'), 'r') as f:
        jsondata = json.load(f)
    return HttpResponse(json.dumps(jsondata), content_type="application/json")


def placeholder_participants(eventid):
    # Get the activity log for the given eventid
    activity_log = R1ActivitiesLog.objects.get(activitieslogid=eventid)

    # Query R2Participants for entries with placeholders and the specified activity log
    participants_with_placeholders = R2Participants.objects.filter(
        activitieslogid=activity_log, 
        placeholder__isnull=False
    ).select_related('placeholder')

    # Extract relevant information
    result = [
        {
            'participantid': participant.placeholder.tempid,
            'participantname': participant.placeholder.surname + ', ' + \
                      participant.placeholder.firstname + ' '+ \
                      participant.placeholder.othername,
            'placeholderid': participant.placeholder.placeholderid,
            'originalid': None,
        }
        for participant in participants_with_placeholders
    ]

    return result


def activity_event_participants(request, activity_type, activity_id):
    #ctr = get_ctr(request)
    #cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.filter(activitytype = activity_type).values()
    event = E2Activities.objects.get(activityid = activity_id)
    organisers = R2Organisers.objects.filter(activity = event.activityid)
    organiser_names = [o.__str__() for o in organisers]
    
    events = ActivitySummary.objects.all() \
    .filter(activityid=activity_id) \
    .values('activitydate','eventid') \
    .annotate(
        total=Count('activityid'),
    )

    output = {
            'activity': list(activity)[0],
            'activitylabel': event.activity,
            'activitycentre': event.centre.centre,
            'activityorgs': organiser_names,
            'activityid': event.activityid,
            'events': []
        }

    for event in events:
        event['activitydate'] = event['activitydate'].strftime('%Y-%m-%d')
        participants = ActivitySummary.objects \
        .values('participantid','participantname','participantcategory','participantgroup') \
        .filter(activitytype=activity_type, eventid=event['eventid']) \
        .annotate(
            originalid=F('participantid'),
            total=Count('activitytype'),
        )
        placeholders = placeholder_participants(event['eventid'])
        event['participantlist'] = list(participants) + placeholders
        output['events'].append(event)
    
    return output


class ActivityParticipants(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        ctr = 'Vig'
        activity_type = kwargs.get('activity_type')
        activity_id = kwargs.get('activity_id')

        try:
            participants = activity_event_participants(request, activity_type, activity_id)
        except Exception as e:
            return Response(
                {'detail': f'An error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(participants)


def ctr_participants(request, ctr):
    cur_ctr = {} if not ctr else {'person__centre__acronym__iexact': ctr}
    cats = request.GET.getlist('cat')
    filtercats = Q()
    for cat in cats:
        filtercats = filtercats | Q(category__category=cat)
    participants = R3CategoryAssign.objects \
    .values('person_id','person__surname','person__firstname','person__othername') \
    .filter(**cur_ctr) \
    .filter(filtercats) \
    .annotate(
        total=Count('person_id')
    )

    print(request.GET.getlist('s'))
    output = []
    for p in participants:
        outputs = {}
        outputs['participantid'] = p['person_id']
        fullname = p['person__surname']+', '+p['person__firstname']+' '+(p['person__othername'] if p['person__othername'] else '')
        outputs['surname'] = p['person__surname']
        outputs['firstname'] = p['person__firstname']
        outputs['othername'] = p['person__othername']
        outputs['participantname'] = fullname.strip()
        output.append(outputs)
    
    return output
    

class PeopleList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        ctr = kwargs.get('ctr')
        participants = ctr_participants(request, ctr)
        return Response(participants)


class PostAttendance(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        activityid = request.data.get("activityid")
        events = request.data.get("events", [])
        currentdate = request.data.get("currentdate")

        if not activityid:
            return Response({"error": "activityid is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        participants_created = []
        participants_deleted = []
        errors = []

        try:
            # If currentdate is provided, handle only the specific event
            if currentdate:
                event = [event for event in events if event["activitydate"] == currentdate]
                if not event:
                    return Response(
                        {"error": f"No event found for the specified currentdate: {currentdate}."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                # Process only the event for the given date
                self._process_event(
                    request,
                    event[0],
                    activityid,
                    participants_created,
                    participants_deleted,
                    errors
                )
            else:
                # Process all events for the given activity
                for event in events:
                    self._process_event(
                        request,
                        event,
                        activityid,
                        participants_created,
                        participants_deleted,
                        errors
                    )

        except Exception as e:
            errors.append({"error": f"Failed to process events: {str(e)}"})

        # Return summary response
        return Response({
            "created": participants_created,
            "deleted": participants_deleted,
            "errors": errors
        }, status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS)


    def _process_event(self, request, event, activityid, participants_created, participants_deleted, errors):
        activity_log_id = event.get("eventid")  # This corresponds to activitieslogid
        activitydate = event.get("activitydate")  # Date when the event occurs
        participant_list = event.get("participantlist")

        try:
            activity = get_object_or_404(E2Activities, activityid=activityid)
            
            # Check if activity log with the provided activitydate exists; create one if it doesn't
            activity_log, created = R1ActivitiesLog.objects.get_or_create(
                activitydate=activitydate,
                activity_id=activity.activityid,
                #defaults={'activitylabel': activity_label}  # Add other necessary fields here if required
            )

            if created:
                # New activity log was created
                print(f"Created new event with ID {activity_log.activitieslogid}")
            else:
                print(f"Using existing event with ID {activity_log.activitieslogid}")


            # Get the participant IDs from the payload
            participant_ids = [p.get("participantid") for p in participant_list if p.get("participantid")]

            # Delete participants that are no longer in the payload
            existing_participants = R2Participants.objects.filter(activitieslogid=activity_log)
            for participant in existing_participants:
                if participant.person and participant.person.personid not in participant_ids:
                    try:
                        participant.delete()
                        participants_deleted.append({
                            "event_id": activity_log.activitieslogid,
                            "participant_id": participant.person.personid
                        })
                    except Exception as e:
                        errors.append({
                            "event_id": activity_log.activitieslogid,
                            "participant_id": participant.person.personid,
                            "error": f"Error deleting participant: {str(e)}"
                        })

            # Process each participant in the event's participant list
            for participant in event.get("participantlist", []):
                participant_id = participant.get("participantid")  # This corresponds to person
                try:
                    '''
                    person = get_object_or_404(E1People, personid=participant_id)
                    
                    # Prepare data for the serializer
                    participant_data = {
                        'activitieslogid': activity_log.activitieslogid,
                        'person': person.personid,
                        'entryuser': request.user.id
                    }
                    print(participant_data)
                    '''
                    person = E1People.objects.filter(personid=participant_id).first()
                    if person:
                        print(person)
                        # Prepare data for the serializer if person exists
                        participant_data = {
                            'activitieslogid': activity_log.activitieslogid,
                            'person': person.personid,
                            'placeholder': None,
                            'entryuser': request.user.id
                        }
                    else:
                        # If person does not exist, check in UserPlaceholders
                        placeholder = UserPlaceholders.objects.filter(tempid=participant_id).first()
                        if placeholder:
                            # Prepare data for the serializer if placeholder exists
                            participant_data = {
                                'activitieslogid': activity_log.activitieslogid,
                                'person': None,
                                'placeholder': placeholder.placeholderid,
                                'entryuser': request.user.id
                            }
                        else:
                            # Log an error if neither exists
                            errors.append({
                                'event_id': activity_log_id,
                                'participant_id': participant_id,
                                'error': 'Participant does not exist in E1People or UserPlaceholders.',
                                'status': 404
                            })
                            continue  # Skip to the next participant

                    print(participant_data)
                    serializer = ParticipantsSerializer(data=participant_data)

                    if serializer.is_valid():
                        try:
                            # Attempt to save the participant entry
                            participant_instance = serializer.save()
                            participants_created.append({
                                'event_id': activity_log.activitieslogid,
                                'participant_id': person.personid if person else placeholder.placeholderid if placeholder else None,
                            })
                        except IntegrityError as e:
                            # Capture unique constraint violation error
                            errors.append({
                                'event_id': activity_log_id,
                                'participant_id': participant_id,
                                'error': f"This participant is already registered for this activity: {str(e)}",
                                'status': 400
                            })
                    else:
                        # Capture serializer validation errors
                        errors.append({
                            'event_id': activity_log_id,
                            'participant_id': participant_id,
                            'error': serializer.errors,
                            'status': 400
                        })

                except Exception as e:
                    # Capture unexpected errors related to retrieving person
                    errors.append({
                        'event_id': activity_log_id,
                        'participant_id': participant_id,
                        'error': f"Person retrieval error: {str(e)}",
                        'status': 500
                    })

        except Exception as e:
            # Capture unexpected errors related to retrieving activity_log
            errors.append({
                'event_id': activity_log_id,
                'error': f"Activity log retrieval error: {str(e)}",
                'status': 500
            })


class PostPlaceholder(APIView):
    def post(self, request, *args, **kwargs):
        # Map participantid to tempid before validation
        data = request.data.copy()
        data['tempid'] = data['participantid']
        
        # Deserialize the incoming data
        serializer = UserPlaceholdersSerializer(data=data)
        
        if serializer.is_valid():
            # Save the new user placeholder to the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivitiesByOrganiser(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        print(request.user)
        user_level = request.user.userstatus.level
        user_ctr = request.user.userstatus.centre
        if hasattr(request.user, 'userperson'):
            user_person = request.user.userperson.person
        
        if user_level == 3:
            # Get all activities
            organiser_activities = R2Organisers.objects.all().values_list('activity_id', flat=True)
        elif user_level == 2:
            organiser_activities = R2Organisers.objects.filter(person__centre=user_ctr).values_list('activity_id', flat=True)
        elif user_level == 1:
            # Get all activities where the person is an organiser
            if user_person:
                organiser_activities = R2Organisers.objects.filter(person=user_person).values_list('activity_id', flat=True)
            else:
                organiser_activities = None
        else:
            organiser_activities = None

        if user_level == 1:
            # Get the activities filtered by those organiser activities
            activities = E2Activities.objects.filter(activityid__in=organiser_activities)
        elif user_level == 2:
            activities = E2Activities.objects.filter(centre=user_ctr)
        elif user_level == 3:
            activities = E2Activities.objects.all()
        else:
            activities = None

        activities_by_type = {}
        if user_level > 1:
            actype = E2ActivityType.objects.all()
            for act in actype:
                activities_by_type[act.activitytypeid] = []
            
        # Group activities by ActivityTypeID
        for activity in activities:
            activities_by_type.setdefault(activity.activitytype_id, []).append(activity)
        
        # Get all ActivityTypes related to the activities
        activity_types = E2ActivityType.objects.filter(activitytypeid__in=activities_by_type.keys())
        
        # Serialize the ActivityTypes with related activities
        serializer = E2ActivityTypeSerializer(activity_types, many=True, context={'activities_by_type': activities_by_type})
        return Response(serializer.data)


class PostPerson(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        serializer = E1PeopleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEmail(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        email = request.query_params.get('email', None)
        if email:
            exists = E1People.objects.filter(email=email).exists()
            return Response({'exists': exists}, status=status.HTTP_200_OK)
        return Response({'error': 'Email not provided'}, status=status.HTTP_400_BAD_REQUEST)


class CheckNames(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        surname = request.query_params.get('surname', '').strip()
        firstname = request.query_params.get('firstname', '').strip()
        othername = request.query_params.get('othername', '').strip()

        if not surname and not firstname:
            return Response({"error": "Surname and first name are required."}, status=status.HTTP_400_BAD_REQUEST)

        exists = E1People.objects.filter(
            surname__iexact=surname,
            firstname__iexact=firstname,
            othername__iexact=othername
        ).exists()

        return Response({"exists": exists}, status=status.HTTP_200_OK)
    

class CentresList(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)
    
    def get(self, request):
        centres = E5Centres.objects.all()
        serializer = E5CentresSerializer(centres, many=True)
        return Response(serializer.data)
    

@api_view(['GET', 'POST'])
@csrf_exempt
def people_list(request):
    """
    List all people, or create a new person.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)
    
    if request.method == 'GET':
        people = E1People.objects.all()
        serializer = PeopleSerializer(people, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = PeopleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
