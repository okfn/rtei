from __future__ import unicode_literals

from django.db import migrations
from django.contrib.contenttypes.management import create_contenttypes
from django.apps import apps as django_apps
from django.core.management import call_command


def load_collections_from_fixture(apps, schema_editor):

    for app_config in django_apps.get_app_configs():
        create_contenttypes(app_config)

    call_command("loaddata", "0009_collections.json")


class Migration(migrations.Migration):

    dependencies = [
        ('rtei', '0008_auto_20160406_1008'),
    ]

    operations = [
        migrations.RunPython(load_collections_from_fixture),
    ]
