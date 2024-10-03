from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("activity/<str:activity_type>/", views.get_activity_list, name="activity"),
    path("activity/<str:activity_type>/participants/<int:activity_id>/", views.get_participants, name="participants"),
    path("activity/<str:activity_type>/events/<int:activity_id>/", views.get_events, name="events"),
    path("activity/<str:activity_type>/events/<int:activity_id>/participants/<int:event_id>/", views.get_event_participants, name="event_participants"),
    path("participant/<int:participant_id>/", views.get_participant, name="participant"),
    path("category/<str:cat>/", views.get_category_list, name="category"),
    path("group/<int:groupid>/", views.get_group_list, name="group"),
    path("group/which/", views.get_user_group, name="user_group"),
    path("summary/", views.get_summary, name="summary"),
]
