# Generated by Django 4.2.1 on 2023-09-05 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_log_time_sanction_end_time_sanction_start_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='sanctioned',
        ),
        migrations.AlterField(
            model_name='sanction',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]