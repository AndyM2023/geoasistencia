# Generated manually to add schedule_type field to AreaSchedule

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_remove_user_phone_attendance_expected_check_in_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='areaschedule',
            name='schedule_type',
            field=models.CharField(
                choices=[
                    ('default', 'Horario por Defecto'),
                    ('custom', 'Horario Personalizado'),
                    ('none', 'Sin Horario'),
                ],
                default='default',
                max_length=10,
                verbose_name='Tipo de Horario'
            ),
        ),
    ]
