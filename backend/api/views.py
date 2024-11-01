# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, HttpResponse
from backend.models import *
from django.db.models import Count, Q
from backend.context import check_valid_user

from datetime import date, datetime, timedelta
import json, os


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
    
    return HttpResponse(json.dumps(output), content_type="application/json")


def ctr_participants(request, ctr):
    print(ctr)
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
    
    return HttpResponse(json.dumps(output), content_type="application/json")
