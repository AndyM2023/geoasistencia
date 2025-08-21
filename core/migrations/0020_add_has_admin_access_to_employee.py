# Generated manually to add has_admin_access field to Employee model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_remove_cedula_from_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='has_admin_access',
            field=models.BooleanField(
                default=False,
                help_text='¿Este empleado tiene acceso al panel administrativo?',
                verbose_name='Acceso Administrativo'
            ),
        ),
    ]
