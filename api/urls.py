# API URL configuration.
from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from .views import *

# Functions
def _is_admin(user):
    return user.groups.filter(name='admin').exists()

urlpatterns = [
    path('get-games-start-time', get_start_times),
    path('get-available-games', get_available_games),
    path('set-play-ended', login_required(set_play_ended), name='set_play_ended'),
    path('add-student-to-game', login_required(add_student_to_game), name='add_student_to_game'),
    path('get-plays-list', user_passes_test(_is_admin)(get_plays_list), name='get_plays_list'),
    path('get-students-list', user_passes_test(_is_admin)(get_students_list), name='get_students_list'),
    path('get-games-list', user_passes_test(_is_admin)(get_games_list), name='get_games_list'),
    path('get-logs-list', user_passes_test(_is_admin)(get_logs_list), name='get_log_list'),
    path('get-sanctions-list', user_passes_test(_is_admin)(get_sanctions_list), name='get_sanctions_list'),
    path('add-student-to-sanctioned', login_required(add_student_to_sanctioned), name='add_student_to_sanctioned'),
]