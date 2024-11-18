
from django.urls import path
from knox import views as knox_views
from backend.api import views

urlpatterns = [
    path("", views.get_json, name="json"),
    path("activity/<str:activity_type>/events/<int:activity_id>/participants/<int:event_id>/", views.ActivityParticipants.as_view(), name="event_participants"),
    #path("participants/<str:ctr>/", views.ctr_participants, name="ctr_participants"),
    path("people/<str:ctr>/", views.PeopleList.as_view(), name="people"),
    path("mark/", views.PostAttendance.as_view(), name="attendance"),
    path(r'login/', views.LoginView.as_view(), name='knox_login'),
    path(r'logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path(r'logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]
