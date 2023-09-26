# Generated by Django 4.2.1 on 2023-09-26 04:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0005_remove_student_sanctioned_alter_sanction_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='file_route',
            field=models.CharField(default='assets/games-cards/game.png', max_length=255),
        ),
        migrations.AlterField(
            model_name='sanction',
            name='play',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='rental.plays'),
        ),
    ]
