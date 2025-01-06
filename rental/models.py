from django.db import models, transaction
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from supabasecon.client import supabase


class Image(models.Model):
    """Modelo de imagenes"""

    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.image.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        try:
            # First, save the image to a temporary location using Django's default storage
            super().save(*args, **kwargs)

            ### The pylint suggestion is suppresed because path property is defined at runtime
            image_path = self.image.path  # pylint: disable=no-member

            # Determine the content type based on the file extension
            _, ext = (
                self.image.name.rsplit(".", 1)
                if "." in self.image.name
                else (self.image.name, None)
            )

            # Upload the file to Supabase
            with open(image_path, "rb") as f:
                response = supabase.storage.from_("Cyberprepa").upload(
                    file=f,
                    path=self.image.name,
                    file_options={"content-type": f"image/{ext}"},
                )

            # Check the upload status code
            if response.status_code != 200:
                raise Exception(
                    f"Upload failed with status code: {response.status_code}"
                )

        except Exception:
            raise  # Re-raise the exception to propagate the error

    @transaction.atomic
    def delete(self, *args, **kwargs):
        try:
            # Extract image path from the image field
            image_path = self.image.name
            # Delete image from Supabase storage
            response = supabase.storage.from_("Cyberprepa").remove([image_path])

            # Check if the response contains a valid status code inside 'metadata'
            if response and isinstance(response, list):
                # Assume the first item in the response list contains the metadata
                metadata = response[0].get("metadata", {})
                status_code = metadata.get("httpStatusCode")

                if status_code != 200:
                    raise Exception(
                        f"Failed to delete image {image_path} from Supabase. HTTP Status: {status_code}"
                    )
            else:
                raise Exception(f"Unexpected response format: {response}")

            # Call the parent class's delete method to delete the record from the database
            super().delete(*args, **kwargs)

        except Exception as e:
            # Rollback will be triggered automatically due to the atomic block
            raise e


class Student(models.Model):
    """Modelo de estudiante
    Matricula, unica
    Nombre, opcional
    Booleano de si se le olvido su credencial
    Hash de biometricos

    _get_played_today: Regresa el numero de juegos que jugo el dia de hoy
    _get_weekly_plays: Regresa el numero de juegos que jugo en la semana
    _get_sanctions_number: Regresa el numero de sanciones que tiene actualmente
    """

    id = models.CharField(
        primary_key=True, max_length=9, validators=[RegexValidator(r"^[a|l][0-9]{8}$")]
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    forgoten_id = models.BooleanField(default=False)
    hash = models.CharField(max_length=1000, null=True, blank=True)

    def is_playing(self):
        return Play.objects.filter(student=self, ended=False).count() > 0

    def get_active_play(self):
        return Play.objects.filter(student=self, ended=False).first()

    def get_played_today(self):
        current_time = timezone.localtime(timezone.now())
        return Play.objects.filter(student=self, time__date=current_time.date()).count()

    def get_weekly_plays(self):
        today = timezone.localtime(timezone.now())
        # Start of the week (Monday)
        start_of_week = today.combine(
            (today - timezone.timedelta(days=today.weekday())),
            timezone.localtime().min.time(),
        )
        # End of the week (Sunday)
        end_of_week = today.combine(
            (start_of_week + timezone.timedelta(days=6)),
            timezone.localtime().max.time(),
        )
        return Play.objects.filter(
            student=self, time__date__range=[start_of_week, end_of_week]
        ).count()

    def get_sanctions_number(self):
        return Sanction.objects.filter(
            student=self, end_time__gte=timezone.now()
        ).count()

    def get_notices(self):
        """Only notices a year ago from now will be taken into account"""
        return Notice.objects.filter(
            student=self, created_at__gte=timezone.now() - timezone.timedelta(days=365)
        )

    def get_owed_material(self):
        return OwedMaterial.objects.filter(
            student=self,
            delivered__lt=models.F("amount"),
        )

    def __str__(self):
        return str(self.id)


class Game(models.Model):
    """Modelo de juegos
    Nombre, unico
    Booleano de si se muestra en la lista de juegos (Todavía se puede jugar o no)
    Fecha y hora en que el primer estudiante comenzó a jugar
    Ruta de la imagen del juego

    _get_plays: Regresa todos los juegos que se han jugado de este juego
    """

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    show = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    image = models.ForeignKey(
        Image, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    def get_plays(self):
        return Play.objects.filter(game=self, ended=False)

    def end_all_plays(self):
        plays = self.get_plays()
        for play in plays:
            play.ended = True
            play.save()

    def __str__(self):
        return f"{self.name} - {self.start_time}"


class Play(models.Model):
    """Modelo de juegos
    Relacion al estudiante que jugo
    Relacion al juego que se jugo
    Booleano de si terminó su juego y lo regresó
    Fecha y hora en que jugó
    """

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, null=False, blank=False
    )
    game = models.ForeignKey(Game, on_delete=models.PROTECT, null=False, blank=False)
    ended = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.game.name} - {self.time}"


class Notice(models.Model):
    """Modelo de llamadas de atención
    Causa de la llamada de atención
    Partida en la que se le llamó la atención
    Estudiante al que se le llama la atención
    """

    cause = models.CharField(max_length=255, null=False, blank=False)
    play = models.ForeignKey(Play, on_delete=models.PROTECT, null=True, blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, null=False, blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.student} - {self.cause}"


class Material(models.Model):
    """Modelo para guardar registro del tipo de material que existe en Cyber"""

    name = models.CharField(max_length=100, null=False, blank=False)
    amount = models.FloatField(default=0)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}. Amount: {self.amount}"


class OwedMaterial(models.Model):
    """
    Modelo para guardar que un estudiante debe material

    material: Referencia al Material que debe el estudiante
    amount: Cantidad de material que debe el estudiante
    delivered: Cantidad de material que ha entregado el estudiante
    student: Referencia al estudiante que debe el material
    delivery_deadline: Fecha limite para entregar el material,
      en caso de que no se entregue se le sancionará
    """

    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, null=False, blank=False
    )
    amount = models.FloatField(default=1, validators=[MinValueValidator(0.0)])
    delivered = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, null=False, blank=False
    )
    delivery_deadline = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_possible_sanctions(cls) -> models.QuerySet["OwedMaterial"]:
        """
        Get all the **OwedMaterial** that are *past* the *delivery deadline*
        and have *not* been *fully delivered* without associated sanctions
        """
        return cls.objects.filter(
            sanctions__isnull=True,
            delivery_deadline__lt=timezone.now(),
            delivered__lt=models.F("amount"),
        )

    def __str__(self) -> str:
        return f"{self.student.pk} owes {self.amount} {self.material.name}"


class Sanction(models.Model):
    """Modelo de sanciones
    Causa de la sancion, escrita por el usuario
    Relacion a la play en la que se dio la sancion, puede ser null/blank
    Relacion al estudiante que esta siendo sancionado
    Fecha y hora en que se inicia la sancion
    Fecha y hora en que se termina la sancion
    """

    cause = models.CharField(max_length=255, null=False, blank=False)
    play = models.ForeignKey(Play, on_delete=models.PROTECT, null=True, blank=True)
    owed_material = models.ForeignKey(
        OwedMaterial,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sanctions",
    )
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, null=False, blank=False
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return f"{self.student} - {self.start_time} - {self.end_time}"
