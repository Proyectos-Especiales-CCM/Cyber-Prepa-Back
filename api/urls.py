# API URL configuration.
from django.urls import path
from django.contrib.auth.decorators import login_required, user_passes_test
from .views import *

# Functions
def _is_admin(user):
    return user.groups.filter(name='admin').exists()

urlpatterns = [
    path('get-games/', get_games, name='get_games'),
    path('get-games-start-time', get_start_times, name='get_start_times'),
    path('get-players/', get_players, name='get_players'),
    path('get-available-games', get_available_games),
    path('set-play-ended', login_required(set_play_ended), name='set_play_ended'),
    path('add-student-to-game', login_required(add_student_to_game), name='add_student_to_game'),
    path('get-plays-list', login_required(get_plays_list), name='get_plays_list'),
    path('get-students-list', user_passes_test(_is_admin)(get_students_list), name='get_students_list'),
    path('get-games-list', user_passes_test(_is_admin)(get_games_list), name='get_games_list'),
    path('get-logs-list', user_passes_test(_is_admin)(get_logs_list), name='get_log_list'),
    path('get-sanctions-list', login_required(get_sanctions_list), name='get_sanctions_list'),
    path('get-users-list', user_passes_test(_is_admin)(get_users_list), name='get_users_list'),
    path('add-student-to-sanctioned', login_required(add_student_to_sanctioned), name='add_student_to_sanctioned'),
    # Admin CRUD datatables calls
    path('game', user_passes_test(_is_admin)(game), name='game'),
    path('student', user_passes_test(_is_admin)(student), name='student'),
    path('play', login_required(play), name='play'),
    path('user', user_passes_test(_is_admin)(user), name='user'),
    #path('upload-game-image', login_required(upload_game_image), name='upload_game_image'),
    path('user_settings/', login_required(userSettings), name='user_settings'),
    path('update_theme/', login_required(updateTheme), name='update_theme'),
]