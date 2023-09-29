# Views (Logic) for API calls.
from django.http import JsonResponse
from datetime import timedelta
from rental.models import Game, Plays, Student, Log, Sanction

# Index calls
def get_start_times(request):
    if request.method == 'GET':
        try:
            games = Game.objects.filter(show=True).values('start_time')
            data = []
            for game in games:
                original_time = game['start_time']
                subtracted_time = original_time - timedelta(hours=5, minutes=5)
                formatted_time = subtracted_time.strftime('%b %d, %Y %H:%M:%S')
                data.append({'time': formatted_time})
                print(formatted_time)
            return JsonResponse(data, safe=False)
        except:
            return JsonResponse({'status': 'error'})
    
def get_available_games(request):
    if request.method == 'GET':
        try:
            games = Game.objects.filter(show=True).values('available')
            data = []
            for game in games:
                data.append({'available': game['available']})
            print(data)
            return JsonResponse(data, safe=False)
        except:
            return JsonResponse({'status': 'error'})
    
def set_play_ended(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            play = Plays.objects.filter(student__id=student_id).latest('time')
            play.ended = True
            play.save()
            log = Log.objects.create(actionPerformed=f' Termina sesión de juego de: {student_id}', user=request.user)
            log.save()
            return JsonResponse({'status': 'success'})
        except Plays.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Play not found'})
        
def add_student_to_game(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        game_id = request.POST.get('game_id')
        try:
            game = Game.objects.get(id=game_id)
            student, created = Student.objects.get_or_create(id=student_id)
            play = Plays.objects.create(game=game, student=student)
            play.save()
            log = Log.objects.create(actionPerformed=f' Inicia sesión de juego para: {student_id}', user=request.user)
            log.save()
            return JsonResponse({'status': 'success', 'message': 'Student added to the game'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

def add_student_to_sanctioned(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        cause = request.POST.get('cause')
        try:
            student = Student.objects.get(id=student_id)
            sanction = Sanction.objects.create(cause=cause, student=student_id)
            sanction.save()
            return JsonResponse({'status': 'success'})
        except Student.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'})

# Admin CRUD datatables calls
def get_plays_list(request):
    if request.method == 'GET':
        plays = (
            Plays.objects
            .select_related('game')
            .values('id', 'student_id', 'game__name', 'ended', 'time')
        )
        data = {'plays': list(plays)}
        return JsonResponse(data, safe=False)
    
def get_students_list(request):
    if request.method == 'GET':
        students = (
            Student.objects
            .values('id', 'name')
        )
        data = {'students': list(students)}
        return JsonResponse(data, safe=False)
    
def get_games_list(request):
    if request.method == 'GET':
        games = (
            Game.objects
            .values('id', 'name', 'displayName', 'available', 'show')
        )
        data = {'games': list(games)}
        return JsonResponse(data, safe=False)
    
def get_logs_list(request):
    if request.method == 'GET':
        logs = (
            Log.objects
            .select_related('user')
            .values('id', 'actionPerformed', 'user__username', 'time')
        )
        data = {'logs': list(logs)}
        return JsonResponse(data, safe=False)
    
def get_sanctions_list(request):
    if request.method == 'GET':
        sanctions = (
            Sanction.objects
            .select_related('student')
            .values('id', 'cause', 'student__id', 'play_id', 'start_time', 'end_time')
        )
        data = {'sanctions': list(sanctions)}
        return JsonResponse(data, safe=False)
