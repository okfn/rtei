from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.management import update_contenttypes
from django.apps import apps as django_apps
from django.core.management import call_command


def load_stores_from_fixture(apps, schema_editor):

    for app_config in django_apps.get_app_configs():
        update_contenttypes(app_config)

    call_command("loaddata", "0003_data.json")


class Migration(migrations.Migration):
    dependencies = [
        ('rtei', '0003_blogpage_intro'),
    ]

    operations = [
        migrations.RunPython(load_stores_from_fixture),
    ]
