from django.db import models
from user.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Student(models.Model):                                                                    # Modelo de alumnos que juegan
    id = models.CharField(primary_key=True, max_length=9)                                       # Matricula
    name = models.CharField(max_length=100, blank=True)                                         # Nombre, opcional
    hash = models.CharField(max_length=1000, null=False, blank=False)                           # Hash de biometricos

class Plays(models.Model):                                                                      # Modelo de juegos por semana
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=False, blank=False)     # Relacion al estudiante que jugo
    game = models.ForeignKey('Game', on_delete=models.PROTECT, null=False, blank=False)         # Relacion al juego que se jugo
    ended = models.BooleanField(default=False)                                                  # Booleano de si terminó su juego y lo regresó
    time = models.DateTimeField(auto_now_add=True)                                              # Fecha y hora en que jugó

class Game(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)               # Nombre del juego, unico, para identificarlo en cualquier lugar y momento
    displayName = models.CharField(max_length=100, null=False, blank=False)                     # Nombre que se muestra en la lista de juegos
    available = models.BooleanField(default=True)                                               # Booleano de si esta disponible para jugar (No hay ningun estudiante jugando)
    show = models.BooleanField(default=True)                                                    # Booleano de si se muestra en la lista de juegos (Todavía se puede jugar o no)
    start_time = models.DateTimeField(null=True, blank=True)                                    # Fecha y hora en que el primer estudiante comenzó a jugar
    file_route = models.CharField(default='assets/games_cards/game.png', max_length=255)        # Ruta de la imagen del juego

class Sanction(models.Model):
    cause = models.CharField(max_length=255, null=False, blank=False)                           # Causa de la sancion, escrita por el usuario
    play = models.ForeignKey(Plays, on_delete=models.PROTECT, null=True, blank=True)            # Relacion a la play en la que se dio la sancion, puede ser null/blank
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=False, blank=False)     # Relacion al estudiante que esta siendo sancionado
    start_time = models.DateTimeField(auto_now_add=True)                                        # Fecha y hora en que se inicia la sancion
    end_time = models.DateTimeField(null=False, blank=False)                                    # Fecha y hora en que se termina la sancion

class Log(models.Model):
    actionPerformed = models.CharField(max_length=255, null=False, blank=False)                 # Accion realizada por el usuario
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)             # Usuario que realizo la accion
    time = models.DateTimeField(auto_now_add=True)                                              # Fecha y hora en que se realizo la accion

class Setting(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)
	value = models.CharField(max_length=200)

	def __str__(self):
		return self.name

@receiver(post_save, sender=Plays)
def update_game_start_time(sender, instance, **kwargs):
    # Check if there are no other ended plays for the same game
    other_ended_plays = Plays.objects.filter(game=instance.game, ended=False).exclude(id=instance.id).exists()
    if not other_ended_plays and instance.ended:
        instance.game.available = True
        instance.game.save()
    elif not other_ended_plays:
        # Update the related game's 'start_time' field with the current play's 'time'
        instance.game.start_time = instance.time
        instance.game.available = False # Make it unavailable since there is a student playing
        instance.game.save()  # Save the related game with the updated 'start_time'
