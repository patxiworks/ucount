from datetime import date

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import *

admin.site.site_header = "YouCount Manager"
admin.site.site_title = "YouCount Manager"
admin.site.index_title = "Welcome to YouCount Manager"


class MembersInline(admin.TabularInline):
    model = R6ActivityAssign
    extra = 1


class E2ActivitiesAdmin(admin.ModelAdmin):
    model = E2Activities
    list_display = ('description', 'person')
    list_filter = ['activitytype__activitytype']

    ### dynamically add inline
    '''def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        
        if obj and obj.format == 'closed':
            ### Add inline for MembersInline
            inline_instances.append(MembersInline(self.model, self.admin_site))
        else:
            pass
        
        return inline_instances'''

admin.site.register(E2Activities, E2ActivitiesAdmin)


'''@admin.register(E2Activities)
class E2ActivitiesAdmin(admin.ModelAdmin):
    inlines = []
    #inlines = [x for x in listing if E2Activities.format == "closed"]

    def save_model(self, request, obj, form, change):
        inlines = super().save_model(request, obj, form, change)
        if form.cleaned_data.get('format') == 'closed':
            inlines.append(MembersInline)
            
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        inlines = super().formfield_for_choice_field(db_field, request)
        
        def get_inlines(self, request, obj):
            inlines = super().get_inlines(request, obj)
            
            if obj and obj.format != "closed":
                print(obj.format)
                #return [MembersInline]
                inlines.append(MembersInline)
            return []
        
        if db_field.name == "format":
            print('dfadfsa2')
            get_inlines(self, request, E2Activities)
            
        return super().formfield_for_choice_field(db_field, request, **kwargs)'''

class CategoryListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("status")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "cat"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        cats = []
        for c in E3Categories.objects.all():
            cats.append(
                (c.category, _(c.description)),
            )
        return cats

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        persons = []
        ps= []
        # First get list of objects without duplicate categories
        for q in queryset:
            for r3 in R3CategoryAssign.objects.filter(person__personid=q.personid).order_by('-startdate')[:1]:
                if r3: ps.append(r3)
        if self.value():
            for q in ps:
                if q.category.category == self.value():
                    persons.append(q.person.personid)
            return queryset.filter(pk__in=persons)
        else:
            return queryset.all()
    

class CategoryAssignInline(admin.TabularInline):
    model = R3CategoryAssign
    max_num = 2
    extra = 0

class GroupAssignInline(admin.TabularInline):
    model = R4GroupAssign
    max_num = 1
    extra = 0

class AttendedByAssignInline(admin.TabularInline):
    model = R5AttendedByAssign
    fk_name = "attendedby"
    max_num = 1
    extra = 0

@admin.register(E1People)
class E1PeopleAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'group')
    list_filter = [CategoryListFilter]
    inlines = [ CategoryAssignInline, GroupAssignInline, AttendedByAssignInline ]

    def fullname(self, obj):
        qs = R3CategoryAssign.objects.filter(person=obj.personid)
        name = obj.__str__()
        #ss = [item.category.category for item in qs][-1]
        #return name + " ("+ ss +")"
        return name

    def group(self, obj):
        qs = R4GroupAssign.objects.filter(person=obj.personid)
        gr = [item.category.category for item in qs]
        try:
            return gr[-1]
        except IndexError:
            return '-'

    fullname.admin_order_field = 'surname'
        


@admin.register(E2ActivityType)
class E2ActivityTypeAdmin(admin.ModelAdmin):
  def has_module_permission(self, request):
    return False


class ParticipantsInline(admin.TabularInline):
    model = R2Participants
    extra = 1


@admin.register(R1ActivitiesLog)
class R1ActivitiesLogAdmin(admin.ModelAdmin):
    # Open Events
    #inlines = [ ParticipantsInline, ]

    # Set activity field to 
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity":
            kwargs["queryset"] = E2Activities.objects.filter(activitytype__activityformat="open")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(MemberActivities)
class MemberActivitiesAdmin(admin.ModelAdmin):
    # Closed Events
    inlines = [ ParticipantsInline, ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity":
            kwargs["queryset"] = E2Activities.objects.filter(activitytype__activityformat="closed")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(E3Categories)
class E3CategoriesAdmin(admin.ModelAdmin):
  def has_module_permission(self, request):
    return False


@admin.register(E4Groups)
class E4GroupsAdmin(admin.ModelAdmin):
  def has_module_permission(self, request):
    return False
    

'''@admin.register(R6ActivityAssign)
class R6ActivityAssignAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "activity":
            kwargs["queryset"] = E2Activities.objects.filter(format="closed")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    #inlines = [ ParticipantsInline, ]'''
