import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from rental.models import OwedMaterial, Sanction

transaction_logger = logging.getLogger("transactions")


class Command(BaseCommand):
    help = "Executes required daily operations, for more information look at the source code"
    requires_migrations_checks = True

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS(f"Daily operations started at {timezone.now()}")
        )
        ### Starts the Daily operations code ###

        # Get owed materials without sanctions associated and past delivery deadline
        owed_materials = OwedMaterial.get_possible_sanctions()
        sanctions = []
        logs = []
        for om in owed_materials:
            sanction = Sanction(
                cause=f"Material {om.material.name} no regresado a tiempo",
                owed_material=om,
                student=om.student,
                # Approx. 4 years duration
                end_time=timezone.now() + timezone.timedelta(weeks=4 * 12 * 4),
            )
            sanctions.append(sanction)
            logs.append(
                f"Sanction created for student {om.student.pk} due to unreturned material"
            )
        if sanctions:
            Sanction.objects.bulk_create(sanctions)
            for log in logs:
                transaction_logger.info(log)

        ### Ends the Daily operations code ###
        self.stdout.write(
            self.style.SUCCESS(
                f"Daily operations successfully finished at {timezone.now()}"
            )
        )
