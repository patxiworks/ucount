
from django.db.models import Count
from backend.models import E5Centres as Centres, E4Groups as Groups
from backend.models import *

# Context processor: For variables available site-wide


def get_session_var(request):
    level = request.user.userstatus.level
    ctr = None
    grp = None
    session = {}
    session['level'] = level
    ctr = request.user.userstatus.centre
    grp = request.user.userstatus.group
    session['centre'] = ctr.centreid if ctr else None
    session['group'] = grp.groupid if grp else None
    return session

def check_valid_user(request):
    request.session['userstatus'] = get_session_var(request)
    session = request.session['userstatus']
    level = session['level']
    ctrlist = None
    ctrs = None
    grps = None
    ctr = None
    grp = None
    if level == 1:
        # get ctr and grp
        if session['centre'] and session['group']:
            validuser = True
            ctrs = Centres.objects.filter(centreid=session['centre'])
            grps = Groups.objects.filter(groupid=session['group'], centre=session['centre'])
            if not grps:
                validuser = False
        else:
            validuser = False
    elif level == 2:
        # get ctr
        if session['centre']:
            validuser = True
            ctrs = Centres.objects.filter(centreid=session['centre'])
        else:
            validuser = False
    elif level == 3:
        # get all ctr
        ctrs = Centres.objects.filter(centreid=session['centre'])
        ctrlist = Centres.objects.all()
        validuser = True
    else:
        validuser = False
    try:
        ctr = [ctr for ctr in ctrs]
        grp = [grp for grp in grps]
    except:
        pass
    return {'validuser': validuser, 'session': {'level':level, 'centre':ctr, 'ctrlist':ctrlist, 'group':grp}}


def get_ctr(request, value='acronym'):
    validuser = check_valid_user(request)
    #print(validuser)
    if 'session' in validuser:
        if validuser['session']:
            if value == 'centre':
                if validuser['session']['centre']:
                    return validuser['session']['centre'][0].centre
                else:
                    return None
            else:
                if validuser['session']['centre']:
                    return validuser['session']['centre'][0].acronym
                else:
                    return None


def category_counts(req):
    ctr = get_ctr(req)
    cats = E3Categories.objects.all()
    def get_count(cat):
        return ParticipantSummary.objects \
        .filter(participantcentre=ctr, participantcategory=cat) \
        .values('participantid','participantname','participantcategory') \
        .annotate(
            unique=Count('participantid', distinct=True)
        )

    catcounts = {}
    for cat in cats:
        catcounts[cat] = [get_count(cat.category).count(), cat.category]
    return catcounts


def site_variables(request):
    context = {}
    if not request.user.is_anonymous:
        request.session['userstatus'] = get_session_var(request)
        cats = category_counts(request)
        
        context = {
            'baseStr': '',
            'mof': E2ActivityType.objects.all().order_by('activitytypename').values(),
            'cats': cats,
            'catcount': sum(item[0] for item in cats.values()),
            'usercheck': check_valid_user(request),
            'user': request.user,
            'centre': get_ctr(request, 'centre')
        }
    return context
