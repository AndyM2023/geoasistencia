# Generated manually to remove redundant position field from User model

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_add_has_admin_access_to_employee'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='position',
        ),
    ]
