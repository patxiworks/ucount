from django.template.defaulttags import register
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from backend.models import *

from datetime import date

# Create views here.

ctr = 'Vig'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def index(request):
    return render(
        request,
        "backend/layouts/base.html",
        {},
    )

def get_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def fetch_group_name(id):
    data = list(E4Groups.objects.filter(groupid=id).values())
    return data[0]['group']

def fetch_centre_id(ctr):
    data = list(E5Centres.objects.filter(acronym=ctr).values())
    return data[0]['centreid']

def fetch_category_name(cat):
    data = list(E3Categories.objects.filter(category=cat).values())
    return data[0]['description']

def fetch_centre_name(ctr):
    data = list(E5Centres.objects.filter(acronym=ctr).values())
    return data[0]['centre']

def fetch_participant_category(participant_id):
    data = list(ParticipantSummary.objects.filter(participantid=participant_id).values())
    return data[0]['participantcategory'] if data else None

def activity_stats(activity):
    activities = ActivitySummary.objects \
    .values('activityid') \
    .filter(participantcentre=ctr, activitytype=activity) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )

    participants = list(ActivitySummary.objects \
    .values('activitytype') \
    .filter(participantcentre=ctr, activitytype=activity) \
    .annotate(
        unique=Count('participantid', distinct=True)
    ))
    
    return {
        'count': ['Number of activities', activities.count()],
        'average': ['Average attendance', int(sum([v['unique'] for v in activities])/activities.count()) if activities.count() else 0],
        'total': ['Total attendance', participants[0]['unique'] if len(participants) else 0]
    }


# Get all [unique] activities
def get_activity_list(request, activity_type):
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    activities = ActivitySummary.objects \
    .values('activityname','activityid') \
    .filter(participantcentre=ctr, activitytype=activity_type) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/index.html",
        {
            'flag': 'activities',
            'activity': activity,
            'activitylist': activities,
            'activityStats': activity_stats(activity_type)
        }
    )


# Get all [unique] participants of an activity
def get_participants(request, activity_type, activity_id):
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    participants = ActivitySummary.objects \
    .values('participantname','participantid','participantcategory','participantgroup') \
    .filter(participantcentre=ctr, activitytype=activity_type, activityid=activity_id) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/index.html",
        {
            'flag': 'participants',
            'activity': activity,
            'activitylabel': event.activity,
            'participantlist': participants,
        }
    )


# Get all instances (i.e. events) of an activity
def get_events(request, activity_type, activity_id):
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    events = ActivitySummary.objects.all() \
    .filter(participantcentre=ctr, activityid=activity_id) \
    .values('activitydate','activityid','eventid') \
    .annotate(
        total=Count('activityid'),
    )
    
    return render(
        request,
        "backend/home/index.html",
        {
            'flag': 'events',
            'activity': activity,
            'activitylabel': event.activity,
            'eventlist': events,
        }
    )


# Get all participants of events
def get_event_participants(request, activity_type, activity_id, event_id):
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    eventinfo = R1ActivitiesLog.objects.get(activitieslogid = event_id)
    participants = ActivitySummary.objects \
    .values('participantid','participantname','participantcategory','participantgroup') \
    .filter(participantcentre=ctr, activitytype=activity_type, eventid=event_id) \
    .annotate(
        total=Count('activitytype'),
        #unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/index.html",
        {
            'flag': 'event-participants',
            'activity': activity,
            'activitylabel': event.activity,
            'activitydate': eventinfo.activitydate,
            'participantlist': participants,
        }
    )

def get_summary(request):
    centre = E5Centres.objects.get(acronym=ctr)
    groups = E4Groups.objects.filter(centre=centre.centreid)
    activities = E2ActivityType.objects.all().order_by('activitytypename')
    items = []

    for activity in activities:
        summary = {}
        participants = ActivitySummary.objects \
        .values('activitytype', 'participantgroup') \
        .filter(participantcentre=ctr, activitytype=activity.activitytype) \
        .annotate(
            unique=Count('participantid', distinct=True)
        )
        actgroups = {}
        for p in participants:
            actgroups[p['participantgroup']] = p['unique']

        attendance = list(ActivitySummary.objects \
        .values('activitytype') \
        .filter(participantcentre=ctr, activitytype=activity.activitytype) \
        .annotate(
            unique=Count('participantid', distinct=True)
        ))
        
        act = ActivitySummary.objects \
        .values('activityid') \
        .filter(participantcentre=ctr, activitytype=activity.activitytype) \
        .annotate(
            total=Count('activitytype'),
        )

        summary['activity'] = activity.activitytypename
        summary['count'] = act.count()
        summary['attendance'] = attendance[0]['unique'] if len(participants) else 0
        summary['groups'] = actgroups
        items.append(summary)
    
    return render(
        request,
        "backend/home/summary.html",
        {
            'flag': 'summary',
            'groups': groups,
            'summary': items,
        }
    )


def get_participant(request, participant_id):
    participant = E1People.objects.get(personid=participant_id)
    participantinfo = list(ParticipantSummary.objects \
        .values() \
        .filter(participantid=participant_id) \
        .annotate(
            unique=Count('participantid', distinct=True)
        ))

    return render(
        request,
        "backend/home/profile.html",
        {
            'participant': participant,
            'participantage': get_age(participant.dofb) if participant.dofb else None,
            'category': participantinfo[0]['participantcategory'],
            'centre': fetch_centre_name(participantinfo[0]['participantcentre']),
            'group': participantinfo[0]['participantgroup'],
            'friend': participantinfo[0]['participantfriendname'],
            'friendcat': fetch_participant_category(participantinfo[0]['participantfriendid'])
        }
    )


def get_category_list(request, cat):
    persons = ParticipantSummary.objects \
        .values() \
        .filter(participantcentre=ctr, participantcategory=cat) \
        .annotate(
            unique=Count('participantid', distinct=True)
        )

    category = E3Categories.objects.filter(category=cat)[0]

    people = []
    for person in persons:
        dofb = E1People.objects.values('dofb').get(pk=person['participantid'])['dofb']
        group = E4Groups.objects \
                .values() \
                .exclude(group__isnull=True) \
                .filter(group=person['participantgroup'], centre=fetch_centre_id(ctr))
        group = group[0] if group else None

        item = {}
        item['id'] = person['participantid']
        item['name'] = person['participantname']
        item['age'] = get_age(dofb) if dofb else None
        item['group'] = person['participantgroup']
        item['groupid'] = group['groupid'] if group else None
        item['friend'] = person['participantfriendname']
        item['friendcat'] = fetch_participant_category(person['participantfriendid'])
        people.append(item)
    

    return render(
        request,
        "backend/home/list.html",
        {
            'flag': 'category',
            'category': category.description,
            'categorylist': people
        }
    )


def get_group_list(request, groupid):
    if groupid:
        group = fetch_group_name(groupid)
        persons = ParticipantSummary.objects \
            .values() \
            .filter(participantcentre=ctr, participantgroup=group) \
            .annotate(
                unique=Count('participantid', distinct=True)
            )
    else:
        group = None
        persons = ParticipantSummary.objects \
            .values() \
            .filter(participantcentre=ctr, participantgroup__isnull=True) \
            .annotate(
                unique=Count('participantid', distinct=True)
            )

    people = []
    for person in persons:
        dofb = E1People.objects.values('dofb').get(pk=person['participantid'])['dofb']
        item = {}
        item['id'] = person['participantid']
        item['name'] = person['participantname']
        item['age'] = get_age(dofb) if dofb else None
        item['group'] = person['participantgroup']
        item['category'] = person['participantcategory']
        item['friend'] = person['participantfriendname']
        item['friendcat'] = fetch_participant_category(person['participantfriendid'])
        people.append(item)

    return render(
        request,
        "backend/home/list.html",
        {
            'flag': 'group',
            'category': group,
            'categorylist': people
        }
    )
