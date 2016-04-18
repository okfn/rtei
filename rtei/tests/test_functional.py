import nose
from django_webtest import WebTest


eq_ = nose.tools.eq_


class SiteTestCase(WebTest):
    fixtures = ['fake_docs.json']

    def test_home(self):
        page = self.app.get('/').follow()

        assert 'Homepage' in page

    def test_redirects_to_language_page(self):
        page = self.app.get('/')

        eq_(page.status_int, 302)
        eq_(page.headers['Location'], '/en/')

    def test_translation(self):
        page = self.app.get('/es/')

        assert 'Explore el Mapa' in page
        assert 'Explore the Map' not in page

    def test_language_links(self):
        page = self.app.get('/').follow()

        page_es = page.click(href='/es/')

        assert 'Explore el Mapa' in page_es
        assert 'Explore the Map' not in page_es

    def test_explore_map(self):
        page = self.app.get('/en/explore/map/')

        assert 'Map' in page

    def test_explore_rtei_year(self):
        page = self.app.get('/en/explore/rtei-theme/')

        assert 'Sort by Name' in page

    def test_explore_rtei_country(self):
        page = self.app.get('/en/explore/rtei-country/')

        assert 'RTEI by Country' in page
        assert 'Select a country' in page
        assert 'Overall Index' not in page

    def test_explore_rtei_country_param(self):
        page = self.app.get('/en/explore/rtei-country/', params={'id': 'CL'})

        assert 'RTEI by Country' in page
        assert 'Select a country' not in page
        assert 'Chile' in page
        assert 'Overall Index' in page

    # TODO: check for something relevant once content is in place
    def test_explore_rtei_over_time(self):
        page = self.app.get('/en/explore/rtei-over-time/')

        assert 'RTEI over Time' in page

    def test_resources(self):
        # first page
        page = self.app.get('/en/resources/')

        assert 'All Resources' in page
        self.assertEqual(len(page.context['documents']), 10)

        # second page
        page_two = self.app.get('/en/resources/?page=2')
        self.assertEqual(len(page_two.context['documents']), 2)

    def test_resources_with_filter_with_results(self):
        '''The fixture fake_docs.json has resources with the year 1998.'''
        page = self.app.get('/en/resources/?year=1999')
        self.assertEqual(len(page.context['documents']), 3)

        assert 'All Resources' not in page
        assert 'No resources found that match the selected filters' not in page

    def test_resources_with_filter_no_results(self):
        '''The fixture fake_docs.json doesn't have resources with the year
        2020'''
        page = self.app.get('/en/resources/?year=2020')
        self.assertEqual(len(page.context['documents']), 0)

        assert 'All Resources' not in page
        assert 'No resources found that match the selected filters' in page

    # TODO: check for something relevant once content is in place
    def test_partners(self):
        page = self.app.get('/en/partners/')

        assert 'Partners' in page

    # TODO: check for something relevant once content is in place
    def test_about_us(self):
        page = self.app.get('/en/about/')

        assert 'About' in page

    def test_blog(self):

        page = self.app.get('/en/blog/')

        assert 'Page' in page

    def test_blog_page(self):

        page = self.app.get('/en/blog/test-post-rtei-blog/')

        assert 'This is a test post' in page
