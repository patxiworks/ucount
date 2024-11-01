# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from backend.api import views

urlpatterns = [
    path("", views.get_json, name="json"),
    path("activity/<str:activity_type>/events/<int:activity_id>/participants/<int:event_id>/", views.activity_event_participants, name="event_participants"),
    path("participants/<str:ctr>/", views.ctr_participants, name="ctr_participants"),
]
