from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

from wagtail_feeds.feeds import ExtendedFeed

from search import views as search_views

from rtei import views as rtei_views


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    # url(r'^search/$', search_views.search, name='search'),

    # url(r'', include(wagtail_urls)),
]

urlpatterns += i18n_patterns(
    # These URLs will have /<language_code>/ appended to the beginning
    url(r'^search/$', search_views.search, name='search'),
    url(r'', include(wagtail_urls)),
)

urlpatterns += [
    url(r'^documents/data/latest/', rtei_views.latest_document,
        name="latest_document"),
    url(r'^documents/data/(?P<year>[0-9]{4})/', rtei_views.document_by_year,
        name="document_by_year"),

    url(r'^blog/feed/rss$', ExtendedFeed(), name='blog_rss_feed'),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
