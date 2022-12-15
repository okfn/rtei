from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from rtei.data import get_countries, get_indicators_for_country
from rtei.models import RTEIPage


class Command(BaseCommand):
    help = 'Create custom pages'

    def add_arguments(self, parser):
        parser.add_argument("--test", action='store_true', default=False)
        parser.add_argument("--create", action='store_true', default=False)
        parser.add_argument("--delete", action='store_true', default=False)

    def handle(self, *args, **options):

        test = options['test']
        create = options['create']
        delete = options['delete']
        self.stdout.write(self.style.SUCCESS(f'Custom pages test: {test} create: {create} delete: {delete}'))

        countries = get_countries()
        years = settings.YEARS

        self.stdout.write(self.style.SUCCESS(f' - Countries: {len(countries)}'))
        base_page = RTEIPage.objects.get(slug='rtei-country')
        n = 0
        for year in years:
            # Create a custom year-only page
            if delete:
                pages = RTEIPage.objects.filter(slug=f'{year}')
                self.stdout.write(self.style.SUCCESS(f' - Deleted: {year}'))
                pages.delete()
                continue
            n += 1
            page = RTEIPage(
                slug=f'{year}',
                depth=base_page.depth + 1,
                path=base_page.path + f'{n:04d}',
                # url_path=f'{country_code}-{year}/',
                # url_path_en=f'{country_code}-{year}/',
                show_in_menus=False,
                title=f'RTEI by Year {year}',
                live=True,
                content_type_id=10,
            )
            base_page.add_child(instance=page)
            revision = page.save_revision(
                approved_go_live_at=timezone.now(),
            )
            revision.publish()

        for country_code, country_base in countries.items():
            country_code = country_code.lower()
            self.stdout.write(self.style.SUCCESS(f'   - {country_code} {country_base["name"]}'))
            # if the country has at least one year, use it
            has_data = False
            for year in years:
                country_data = get_indicators_for_country(country_code.upper(), year)
                if country_data:
                    has_data = True
                    break
            else:
                # Non required country,
                continue

            if delete:
                pages = RTEIPage.objects.filter(slug=f'{country_code}')
                self.stdout.write(self.style.SUCCESS(f' - Deleted: {country_code}'))
                pages.delete()
            
            if create:
                n += 1
                page = RTEIPage(
                    slug=f'{country_code}',
                    depth=base_page.depth + 1,
                    path=base_page.path + f'{n:04d}',
                    # url_path=f'{country_code}-{year}/',
                    # url_path_en=f'{country_code}-{year}/',
                    show_in_menus=False,
                    title=f'RTEI by Country {country_base["name"]}',
                    live=True,
                    content_type_id=10,
                )
                base_page.add_child(instance=page)
                revision = page.save_revision(
                    approved_go_live_at=timezone.now(),
                )
                revision.publish()

            for year in years:
                country_data = get_indicators_for_country(country_code.upper(), year)
                if not country_data:
                    continue
                pages = RTEIPage.objects.filter(
                    slug=f'{country_code}-{year}',
                )
                page_exists = pages.count() > 0
                if page_exists:
                    self.stdout.write(self.style.SUCCESS(f'     - {year} EXISTS'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'     - {year} NOT EXISTS'))
                
                if test:
                    continue

                if delete:
                    if page_exists:
                        pages.delete()
                        self.stdout.write(self.style.SUCCESS('       - DELETED'))
                    else:
                        self.stdout.write(self.style.SUCCESS('       - Nothing to delete'))
                    continue

                if not create:
                    raise Exception('Unexpected params, --test, --create or --delete must be set')

                n += 1
                page = RTEIPage(
                    slug=f'{country_code}-{year}',
                    depth=base_page.depth + 1,
                    path=base_page.path + f'{n:04d}',
                    # url_path=f'{country_code}-{year}/',
                    # url_path_en=f'{country_code}-{year}/',
                    show_in_menus=False,
                    title=f'RTEI by Country {country_base["name"]} {year}',
                    live=True,
                    content_type_id=10,
                )
                base_page.add_child(instance=page)
                revision = page.save_revision(
                    approved_go_live_at=timezone.now(),
                )
                revision.publish()
