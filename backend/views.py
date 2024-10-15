from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaulttags import register
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db.models import Count
from backend.models import *
from backend.context import get_ctr, check_valid_user

from datetime import date, datetime, timedelta

# Create views here.

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

def user_level_check(user):
    return user.userstatus.level > 0

def login(request):
    return render(
        request,
        "backend/home/login.html",
        {},
    )

def get_age(dateborn):
    today = date.today()
    return today.year - dateborn.year - ((today.month, today.day) < (dateborn.month, dateborn.day))

def fetch_group_name(id):
    data = list(E4Groups.objects.filter(groupid=id).values())
    return data[0]['group'] if data else None

def fetch_group_id(group, ctr_id):
    data = list(E4Groups.objects.filter(group=group, centre=ctr_id).values())
    return data[0]['groupid'] if data else 0

def fetch_centre_id(ctr):
    data = list(E5Centres.objects.filter(acronym=ctr).values())
    return data[0]['centreid'] if data else None

def fetch_category_name(cat):
    data = list(E3Categories.objects.filter(category=cat).values())
    return data[0]['description'] if data else None

def fetch_centre_name(ctr):
    data = list(E5Centres.objects.filter(acronym=ctr).values())
    return data[0]['centre'] if data else None

def fetch_participant_category(participant_id):
    data = list(ParticipantSummary.objects.filter(participantid=participant_id).values())
    return data[0]['participantcategory'] if data else None

def fetch_friend_info(participantid):
    friend = list(ParticipantSummary.objects \
                    .values() \
                    .filter(participantfriendid=participantid))
        
    friendname = friend[0]['participantname'] if friend else None
    friendid = friend[0]['participantid'] if friend else None
    friendcat = fetch_participant_category(friendid)

    return {
        'id': friendid,
        'name': friendname,
        'cat': friendcat
    }

def activity_stats(activity, ctr):
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activities = ActivitySummary.objects \
    .values('activityid') \
    .filter(**cur_ctr) \
    .filter(activitytype=activity) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )

    participants = list(ActivitySummary.objects \
    .values('activitytype') \
    .filter(**cur_ctr) \
    .filter(activitytype=activity) \
    .annotate(
        unique=Count('participantid', distinct=True)
    ))
    
    return {
        'count': ['Number of activities', activities.count()],
        'average': ['Average attendance', int(sum([v['unique'] for v in activities])/activities.count()) if activities.count() else 0],
        'total': ['Total attendance', participants[0]['unique'] if len(participants) else 0]
    }


def chart_data(participant_id, ctr):
    activities = E2ActivityType.objects.all().order_by('activitytypename')
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    items = []
    for activity in activities:
        item = {}
        entries = list(ActivitySummary.objects \
        .values('activitydate','activityenddate') \
        .filter(**cur_ctr) \
        .filter(participantid=participant_id, activitytype=activity.activitytype))

        dates = []
        for entry in entries:
            if 'activitydate' in entry:
                if entry['activityenddate']:
                    delta = entry['activityenddate'] - entry['activitydate']
                    for i in range(delta.days + 1):
                        day = entry['activitydate'] + timedelta(days=i)
                        dates.append(day.strftime('%m/%d/%y'))
                else:
                    dates.append(entry['activitydate'].strftime('%m/%d/%y'))
        
        item['name'] = activity.activitytype
        item['fname'] = activity.activitytypename
        item['pattern'] = {}
        item['pattern']['date'] = dates
        #item['pattern']['date'] = [entry['activitydate'].strftime('%m/%d/%y') for entry in entries if 'activitydate' in entry]
        items.append(item)
    return items


def dashboard_data(ctr):
    activities = E2ActivityType.objects.all().order_by('activitytypename')
    cur_ctr = {} if not ctr else {'activitycentre': ctr}
    items = []
    for activity in activities:
        entries = list(ActivitySummary.objects \
            .values('activitydate') \
            .filter(**cur_ctr) \
            .filter(activitytype=activity.activitytype, activitydate__year=datetime.now().year))

        counts = dict()
        # get list of months (by number)
        months = [d['activitydate'].month for d in entries if 'activitydate' in d]
        # count the occurrence of months and place in dict
        for i in months:
            counts[i] = counts.get(i, 0) + 1
        # include values for other months (set them to 0)
        allmonths = {x:counts[x] if x in counts else 0 for x in list(range(1, 13))}

        info = {}
        info['months'] = months
        info['counts'] = list(allmonths.values())
        info['code'] = activity.activitytype
        info['activity'] = activity.activitytypename
        items.append(info)

    return items


def birthday_list(people, which='any'):
    if which == 'today':
        persons = people.filter(dofb__month=datetime.now().month, dofb__day=datetime.now().day).values('personid','dofb')
    else:
        persons = people.filter(dofb__month=datetime.now().month).values('personid','dofb')
    items = []
    for person in persons:
        item = {}
        item['id'] = person['personid']
        item['dob'] = person['dofb']
        item['age'] = get_age(person['dofb'])
        entries = ParticipantSummary.objects \
                  .values('participantname','participantcategory','participantgroup') \
                  .filter(participantid=person['personid'])
        item['info'] = list(entries)
        items.append(item)
            
    return items


@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def index(request):
    ctr = get_ctr(request)
    if ctr:
        ctrid = fetch_centre_id(ctr)
        people = E1People.objects.filter(centre=ctrid)
        activities = E2Activities.objects.filter(centre=ctrid)
    else:
        people = E1People.objects.all()
        activities = E2Activities.objects.all()        

    activitydata = dashboard_data(ctr)
    data = [x['counts'] for x in activitydata]
    month_totals = [sum(item) for item in zip(*data)]
    activity_avg = [sum(item) for item in data]

    return render(
        request,
        "backend/home/index.html",
        {
            'year': datetime.now().year,
            'chartdata': dashboard_data(ctr),
            'chartcounter': range(0,6),
            'birthdays': birthday_list(people, 'today'),
            'birthdays_month': birthday_list(people),
            'people_count': people.count(),
            'activity_count': activities.count(),
            'month_avg_att': sum(month_totals)/len(month_totals) if month_totals else 0,
            'activity_avg': sum(activity_avg)/len(activity_avg) if activity_avg else 0
        },
    )


def get_user_group(request):
    groupid = None
    ctrid = None
    try:
        groupid = request.user.userstatus.group.groupid
        ctrid = request.user.userstatus.centre.centreid
    except:
        pass
    if groupid:
        return redirect("/group/"+str(groupid)+"/")
    else:
        return HttpResponse("There was a problem loading the page. Please contact the admin.")


# Get all [unique] activities
@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_activity_list(request, activity_type):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    activities = ActivitySummary.objects \
    .values('activityname','activityid') \
    .filter(**cur_ctr) \
    .filter(activitytype=activity_type) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/activity.html",
        {
            'flag': 'activities',
            'activity': activity,
            'activitylist': activities,
            'activityStats': activity_stats(activity_type, ctr)
        }
    )


# Get all [unique] participants of an activity
@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_participants(request, activity_type, activity_id):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    participants = ActivitySummary.objects \
    .values('participantname','participantid','participantcategory','participantgroup') \
    .filter(**cur_ctr) \
    .filter(activitytype=activity_type, activityid=activity_id) \
    .annotate(
        total=Count('activitytype'),
        unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/activity.html",
        {
            'flag': 'participants',
            'activity': activity,
            'activitylabel': event.activity,
            'participantlist': participants,
        }
    )


# Get all instances (i.e. events) of an activity
@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_events(request, activity_type, activity_id):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    events = ActivitySummary.objects.all() \
    .filter(**cur_ctr) \
    .filter(activityid=activity_id) \
    .values('activitydate','activityid','eventid') \
    .annotate(
        total=Count('activityid'),
    )
    
    return render(
        request,
        "backend/home/activity.html",
        {
            'flag': 'events',
            'activity': activity,
            'activitylabel': event.activity,
            'eventlist': events,
        }
    )


# Get all participants of events
@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_event_participants(request, activity_type, activity_id, event_id):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    activity = E2ActivityType.objects.get(activitytype = activity_type)
    event = E2Activities.objects.get(activityid = activity_id)
    eventinfo = R1ActivitiesLog.objects.get(activitieslogid = event_id)
    participants = ActivitySummary.objects \
    .values('participantid','participantname','participantcategory','participantgroup') \
    .filter(**cur_ctr) \
    .filter(activitytype=activity_type, eventid=event_id) \
    .annotate(
        total=Count('activitytype'),
        #unique=Count('participantid', distinct=True)
    )
    
    return render(
        request,
        "backend/home/activity.html",
        {
            'flag': 'event-participants',
            'activity': activity,
            'activitylabel': event.activity,
            'activitydate': eventinfo.activitydate,
            'participantlist': participants,
        }
    )

@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_summary(request):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    if ctr:
        centre = E5Centres.objects.get(acronym=ctr)
        groups = list(E4Groups.objects.filter(centre=centre.centreid).values('group'))
        groups.append({'group':None}) # for participants without groups
    else:
        userinfo = check_valid_user(request)
        ctrlist = list(userinfo['session']['ctrlist'])
        groups = [{'group':item.acronym} for item in ctrlist]
    activities = E2ActivityType.objects.all().order_by('activitytypename')
    items = []

    for activity in activities:
        summary = {}
        if ctr:
            fieldlist = ['activitytype', 'participantgroup']
            pivot = 'participantgroup'
        else:
            fieldlist = ['activitytype', 'participantcentre']
            pivot = 'participantcentre'
        participants = ActivitySummary.objects \
            .values(*fieldlist) \
            .filter(**cur_ctr) \
            .filter(activitytype=activity.activitytype) \
            .annotate(
                unique=Count('participantid', distinct=True)
        )
        #print(participants)
        actgroups = {}
        for p in participants:
            actgroups[p[pivot]] = p['unique']

        attendance = list(ActivitySummary.objects \
            .values('activitytype') \
            .filter(**cur_ctr) \
            .filter(activitytype=activity.activitytype) \
            .annotate(
                unique=Count('participantid', distinct=True)
            )
        )
        #print(attendance)
        
        act = ActivitySummary.objects \
            .values('activityid') \
            .filter(**cur_ctr) \
            .filter(activitytype=activity.activitytype) \
            .annotate(
                total=Count('activitytype'),
            )
        #print(act)

        summary['activity'] = activity.activitytypename
        summary['count'] = act.count()
        summary['attendance'] = attendance[0]['unique'] if len(participants) else 0
        summary['groups'] = actgroups
        items.append(summary)
        #print(summary)
    
    return render(
        request,
        "backend/home/summary.html",
        {
            'flag': 'summary',
            'groups': groups,
            'summary': items,
        }
    )


@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_participant(request, participant_id):
    ctr = get_ctr(request)
    participant = E1People.objects.get(personid=participant_id)
    participantinfo = list(ParticipantSummary.objects \
        .values() \
        .filter(participantid=participant_id) \
        .annotate(
            unique=Count('participantid', distinct=True)
        ))
    
    friend = fetch_friend_info(participantinfo[0]['participantid'])
    centre_name = fetch_centre_name(participantinfo[0]['participantcentre'])
    
    return render(
        request,
        "backend/home/profile.html",
        {
            'participant': participant,
            'participantage': get_age(participant.dofb) if participant.dofb else None,
            'category': participantinfo[0]['participantcategory'],
            'centre': centre_name,
            'group': participantinfo[0]['participantgroup'],
            'groupid': fetch_group_id(participantinfo[0]['participantgroup'], fetch_centre_id(participantinfo[0]['participantcentre'])),
            'friend': friend['name'],
            'friendcat': friend['cat'],
            'friendid': friend['id'],
            'chartdata': chart_data(participantinfo[0]['participantid'], participantinfo[0]['participantcentre']),
        }
    )


@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_category_list(request, cat):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    persons = ParticipantSummary.objects \
        .values() \
        .filter(**cur_ctr) \
        .filter(participantcategory=cat) \
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

        friend = fetch_friend_info(person['participantid'])

        item = {}
        item['id'] = person['participantid']
        item['name'] = person['participantname']
        item['centre'] = person['participantcentre']
        item['age'] = get_age(dofb) if dofb else None
        item['group'] = person['participantgroup']
        item['groupid'] = group['groupid'] if group else None
        item['friend'] = friend['name']
        item['friendid'] = friend['id']
        item['friendcat'] = friend['cat']
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


@login_required(login_url="/login/")
@user_passes_test(user_level_check, redirect_field_name=None, login_url="/group/which/")
def get_group_list(request, groupid):
    ctr = get_ctr(request)
    cur_ctr = {} if not ctr else {'participantcentre': ctr}
    if groupid:
        group = fetch_group_name(groupid)
        persons = ParticipantSummary.objects \
            .values() \
            .filter(**cur_ctr) \
            .filter(participantgroup=group) \
            .annotate(
                unique=Count('participantid', distinct=True)
            )
    else:
        group = None
        persons = ParticipantSummary.objects \
            .values() \
            .filter(**cur_ctr) \
            .filter(participantgroup__isnull=True) \
            .annotate(
                unique=Count('participantid', distinct=True)
            )

    people = []
    for person in persons:
        friend = fetch_friend_info(person['participantid'])
        dofb = E1People.objects.values('dofb').get(pk=person['participantid'])['dofb']
        item = {}
        item['id'] = person['participantid']
        item['name'] = person['participantname']
        item['age'] = get_age(dofb) if dofb else None
        item['centre'] = person['participantcentre']
        item['group'] = person['participantgroup']
        item['category'] = person['participantcategory']
        item['friend'] = friend['name']
        item['friendid'] = friend['id']
        item['friendcat'] = friend['cat']
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
