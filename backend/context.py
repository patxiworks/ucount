
from django.db.models import Count
from backend.models import *

# Context processor: For variables available site-wide

ctr = 'Vig'

def category_counts():
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
    cats = category_counts()
    context = {
        'baseStr': '/app',
        'mof': E2ActivityType.objects.all().order_by('activitytypename').values(),
        'cats': category_counts(),
        'catcount': sum(item[0] for item in cats.values())
    }
    return context
