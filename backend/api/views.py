from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db.models import Count, Q

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
    with open(os.path.join(BASE_DIR, 'static/backend/assets/testdata.json'), 'r') as f:
        jsondata = json.load(f)
    return HttpResponse(json.dumps(jsondata), content_type="application/json")


def activity_event_participants(request, activity_type, activity_id, event_id):
    #ctr = get_ctr(request)
    #cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.filter(activitytype = activity_type).values()
    event = E2Activities.objects.get(activityid = activity_id)
    eventinfo = R1ActivitiesLog.objects.get(activitieslogid = event_id)
    
    events = ActivitySummary.objects.all() \
    .filter(activityid=activity_id) \
    .values('activitydate','eventid') \
    .annotate(
        total=Count('activityid'),
    )

    output = {
            'activity': list(activity),
            'activitylabel': event.activity,
            'activityid': event.activityid,
            'events': []
        }

    for event in events:
        event['activitydate'] = event['activitydate'].strftime('%Y-%m-%d')
        participants = ActivitySummary.objects \
        .values('participantid','participantname','participantcategory','participantgroup') \
        .filter(activitytype=activity_type, eventid=event['eventid']) \
        .annotate(
            total=Count('activitytype'),
        )
        event['participantlist'] = list(participants)
        output['events'].append(event)
    
    #print(output)
    
    #return HttpResponse(json.dumps(output), content_type="application/json")
    return output


class ActivityParticipants(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        ctr = 'Vig'
        activity_type = kwargs.get('activity_type')
        activity_id = kwargs.get('activity_id')
        event_id = kwargs.get('event_id')
        participants = activity_event_participants(request, activity_type, activity_id, event_id)
        return JsonResponse(participants, safe=False)


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
        outputs['participantname'] = p['person__surname']+', '+p['person__firstname']
        output.append(outputs)
    
    #return HttpResponse(json.dumps(output), content_type="application/json")
    return output
    

class PeopleList(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        ctr = kwargs.get('ctr')
        participants = ctr_participants(request, ctr)
        return JsonResponse(participants, safe=False)


def post_attendance(model):
    event = R1ActivitiesLog.objects.get(pk=3)
    attendee = E1People.objects.get(pk=12)
    #q = model(activitieslogid=event, person=attendee)
    #q.save()
    return '{"activitieslogid": 3, "person": 12}'


class PostAttendance2(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        activityid = request.data.get("activityid")
        events = request.data.get("events", [])
        currentdate = request.data.get("currentdate")
        print(currentdate)
        participants_created = []
        errors = []

        for event in events:
            activity_log_id = event.get("eventid")  # This corresponds to activitieslogid
            activitydate = event.get("activitydate")  # Date when the event occurs

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

                # Process each participant in the event's participant list
                for participant in event.get("participantlist", []):
                    participant_id = participant.get("participantid")  # This corresponds to person
                    try:
                        person = get_object_or_404(E1People, personid=participant_id)

                        # Prepare data for the serializer
                        participant_data = {
                            'activitieslogid': activity_log.activitieslogid,
                            'person': person.personid
                        }
                        serializer = ParticipantsSerializer(data=participant_data)

                        if serializer.is_valid():
                            try:
                                # Attempt to save the participant entry
                                participant_instance = serializer.save()
                                participants_created.append(serializer.data)
                            except IntegrityError:
                                # Capture unique constraint violation error
                                errors.append({
                                    'activity_log_id': activity_log_id,
                                    'participant_id': participant_id,
                                    'error': 'This participant is already registered for this activity.',
                                    'status': 400
                                })
                        else:
                            # Capture serializer validation errors
                            errors.append({
                                'activity_log_id': activity_log_id,
                                'participant_id': participant_id,
                                'error': serializer.errors,
                                'status': 400
                            })

                    except Exception as e:
                        # Capture unexpected errors related to retrieving person
                        errors.append({
                            'activity_log_id': activity_log_id,
                            'participant_id': participant_id,
                            'error': f"Person retrieval error: {str(e)}",
                            'status': 500
                        })

            except Exception as e:
                # Capture unexpected errors related to retrieving activity_log
                errors.append({
                    'activity_log_id': activity_log_id,
                    'error': f"Activity log retrieval error: {str(e)}",
                    'status': 500
                })

        # Return a summary of all created entries and any errors encountered
        return Response({
            'created': participants_created,
            'errors': errors
        }, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)
    

class PostAttendance(APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        activityid = request.data.get("activityid")
        events = request.data.get("events", [])
        currentdate = request.data.get("currentdate")
        print(currentdate)

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


    def _process_event(self, event, activityid, participants_created, participants_deleted, errors):
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
                if participant.person.personid not in participant_ids:
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
                    person = get_object_or_404(E1People, personid=participant_id)

                    # Prepare data for the serializer
                    participant_data = {
                        'activitieslogid': activity_log.activitieslogid,
                        'person': person.personid
                    }
                    serializer = ParticipantsSerializer(data=participant_data)

                    if serializer.is_valid():
                        try:
                            # Attempt to save the participant entry
                            participant_instance = serializer.save()
                            participants_created.append({
                                'event_id': activity_log.activitieslogid,
                                'participant_id': person.personid,
                            })
                        except IntegrityError:
                            # Capture unique constraint violation error
                            errors.append({
                                'event_id': activity_log_id,
                                'participant_id': participant_id,
                                'error': 'This participant is already registered for this activity.',
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
    
