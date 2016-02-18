import nose
from django_webtest import WebTest


eq_ = nose.tools.eq_


class SiteTestCase(WebTest):

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
        page = self.app.get('/en/explore/rtei-year/')

        assert 'RTEI by Year' in page

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

    def test_explore_rtei_over_time(self):
        page = self.app.get('/en/explore/rtei-over-time/')

        assert 'RTEI over Time' in page

    def test_resources(self):
        page = self.app.get('/en/resources/')

        assert 'Resources' in page

    def test_partners(self):
        page = self.app.get('/en/partners/')

        assert 'Partners' in page

    def test_contact_us(self):
        page = self.app.get('/en/contact-us/')

        assert 'Contact Us' in page

    def test_about_us(self):
        page = self.app.get('/en/about-us/')

        assert 'About Us' in page
