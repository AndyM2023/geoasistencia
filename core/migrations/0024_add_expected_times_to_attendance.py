# Generated manually to add expected times to Attendance model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_add_schedule_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='expected_check_in',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora de Entrada Esperada'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='expected_check_out',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora de Salida Esperada'),
        ),
    ]
