from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from rtei.models import RTEIPage


class Command(BaseCommand):
    help = 'Create custom pages for maps'

    def add_arguments(self, parser):
        parser.add_argument("--create", action='store_true', default=True)
        parser.add_argument("--delete", action='store_true', default=False)

    def handle(self, *args, **options):

        create = options['create']
        delete = options['delete']
        self.stdout.write(self.style.SUCCESS(f'Custom pages map, create: {create} delete: {delete}'))

        years = settings.YEARS
        base_page = RTEIPage.objects.get(slug='map')
        n = 0
        for year in years:
            # Create a custom year-only page
            n += 1
            slug = f'map-{year}'
            if delete:
                self.stdout.write(self.style.SUCCESS(f'Deleting map {year}'))
                page = RTEIPage.objects.get(slug=slug)
                page.delete()
                continue
            
            self.stdout.write(self.style.SUCCESS(f'Creating map {year}'))
            page = RTEIPage(
                slug=slug,
                depth=base_page.depth + 1,
                path=base_page.path + f'{n:04d}',
                show_in_menus=False,
                title=f'RTEI map by Year {year}',
                live=True,
                content_type_id=10,
            )
            base_page.add_child(instance=page)
            revision = page.save_revision(
                approved_go_live_at=timezone.now(),
            )
            revision.publish()
