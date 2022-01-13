from bakery.views import BuildableDetailView

#from wagtail.wagtailcore.views import serve
#from wagtail.wagtailcore.middleware import SiteMiddleware
#from wagtail.wagtailcore.models import Site

from wagtail.core.views import serve
from wagtail.core.middleware import SiteMiddleware
from wagtail.core.models import Site

class BakeryView(BuildableDetailView):
    """
    An abstract class that can be inherited to create a buildable view that can be
    added to BAKERY_VIEWS setting. An inheriting class should define a bakery_model
    property pointing to a Wagtail Page model.

    Example:

        # File: app/models.py

        from wagtail.wagtailcore.pages import Page

        class AuthorPage(Page):
            bakery_views = ('app.bakery_views.AuthorPage',)
            ...

        # File: app/bakery_views.py

        from wagtail.wagtailbakery.views import BakeryView
        from . import models

        class AuthorPage(BakeryView):
            bakery_model = models.AuthorPage

        # File: project/settings.py:

        BAKERY_VIEWS = (
            'app.bakery_views.AuthorPage',
            ...
        )

        BUILD_DIR = os.path.join(PROJECT_ROOT, 'baked')

    Build command:

        python manage.py build app.bakery_views.AuthorPage

    """

    bakery_model = None

    def get_queryset(self):
        """
        Defines get_queryset() for BuildableDetailView to return a
        QuerySet containing all live Wagtail Page models
        """
        return self.bakery_model.objects.live()

    def get(self, request):
        """
        Overrides DetailView's get() to return TemplateResponse from serve()
        after passing request through Wagtail SiteMiddleware
        """
        smw = SiteMiddleware()
        smw.process_request(request)
        response = serve(request, request.path)
        return response

    def get_content(self):
        """
        Overrides BuildableMixin's get_content() to work with
        both TemplateRespose and HttpResponse
        """
        response = self.get(self.request)
        if hasattr(response, 'render'):
            response = response.render()
        return response.content

    def get_url(self, obj):
        """
        Overrides BuildableDetailView's get_url() to return a url from the
        Page model url_path property
        """
        root_path = Site.get_site_root_paths()
        if len(root_path):
            root_path = root_path[0][1]
            if obj.url_path == root_path:
                return '/'
            elif root_path in obj.url_path:
                if obj.url_path.index(root_path) == 0:
                    return obj.url.replace(root_path, '/', 1)
        return obj.url_path

    class Meta:
        abstract = True

