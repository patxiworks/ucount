
from django.urls import path
from knox import views as knox_views
from backend.api import views

urlpatterns = [
    path("", views.get_json, name="json"),
    path('activities/', views.ActivitiesByOrganiser.as_view(), name='activities-by-organiser'),
    path("activity/<str:activity_type>/events/<int:activity_id>/", views.ActivityParticipants.as_view(), name="event_participants"),
    path("events/<int:activity_id>/", views.EventsList.as_view(), name='events'),
    path('add/participant/<int:activitieslogid>/', views.AddParticipant.as_view(), name='check-email-add-participant'),
    path("people/", views.PeopleList.as_view(), name="people"),
    path("people/<str:ctr>/", views.PeopleList.as_view(), name="ctr-people"),
    path("add/attendance/", views.PostAttendance.as_view(), name="attendance"),
    path("add/placeholder/", views.PostPlaceholder.as_view(), name="placeholder"),
    path('add/person/', views.PostPerson.as_view(), name='add-person'),
    path('update/participant/<int:placeholderid>/<int:personid>/', views.UpdateParticipant.as_view(), name='update-participant'),
    path('validate/email/', views.CheckEmail.as_view(), name='check-email'),
    path('validate/names/', views.CheckNames.as_view(), name='check-names'),
    path('centres/', views.CentresList.as_view(), name='centres'),
    
    path(r'login/', views.LoginView.as_view(), name='knox_login'),
    path(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),

    path("sample/", views.get_json, name="sample_json"),
]
