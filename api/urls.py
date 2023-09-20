# API URL configuration.
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [
    path('get-games-start-time', get_start_times),
    path('set-play-ended', login_required(set_play_ended), name='set_play_ended'),
    path('add-student-to-game', login_required(add_student_to_game), name='add_student_to_game'),
    path('get-plays-list', login_required(get_plays_list), name='get_plays_list'),
]