import imp
import os
import logging
from mock import patch, MagicMock
from www.redirect import redirect_if_needed


utils = imp.load_source('utils', os.path.join(os.path.dirname(__file__), 'utils.py'))


log = logging.getLogger(__name__)


class Test(utils.Test):

    def setUp(self):
        super(Test, self).setUp()


    def test_ping_does_not_redirect_to_https(self):
        if self.port == '8080':
            return

        self._assertMethodReturnContent(
            '/ping',
            'GET',
            {},
            200,
            None,
            None,
            allow_redirects=False,
            verify_ssl=False,
            port=80
        )

    def assertGetRedirectsToHttps(self, path, same_path=True, code=301):
        r = self._assertMethodReturnContent(
            path,
            'GET',
            {},
            code,
            None,
            None,
            allow_redirects=False,
            verify_ssl=False,
            port=80
        )

        http_url = r.url
        https_url = http_url.replace('http', 'https').replace(':80', '')
        redirect_url = r.headers.get('Location')
        if same_path:
            self.assertEqual(redirect_url.lower(), https_url.lower())
        self.assertTrue('https' in redirect_url)
        return redirect_url


    def test_version_does_redirect_to_https(self):
        if self.port == '8080' or '172.17.0' in self.host:
            return
        self.assertGetRedirectsToHttps('/version', same_path=True, code=302)
        self.assertGetRedirectsToHttps('/auth/version', same_path=True, code=302)


    def test_landing_page_redirect_to_https(self):
        if self.port == '8080' or '172.17.0' in self.host:
            return
        url = self.assertGetRedirectsToHttps('/', same_path=False, code=302)
        self.assertTrue(url.endswith('.com/sv'), "%s ends with .com/sv" % url)


    @patch("www.localisation.request")
    @patch("www.redirect.request")
    @patch("www.redirect.redirect")
    @patch("www.redirect.is_https_request")
    def test_redirects(self, s, r, m1, m2):

        tests = [
            # url, redirected?, redirect_code, redirect_url

            # Api calls not redirected
            ['https://127.0.0.1/v1/foo/bar', False, None, None],
            ['https://bazardelux.com/v1/whatever', False, None, None],
            ['http://127.0.0.1/v1/foo/bar', False, None, None],
            ['http://bazardelux.com/v1/whatever', False, None, None],

            # Direct calls not redirected
            ['http://127.0.0.1/whatever', False, None, None],
            ['http://172.17.0.2/whatever', False, None, None],
            ['http://1.2.3.4/whatever', False, None, None],
            ['http://localhost/whatever', False, None, None],
            ['https://127.0.0.1/whatever', False, None, None],
            ['https://172.17.0.2/whatever', False, None, None],
            ['https://1.2.3.4/whatever', False, None, None],
            ['https://localhost/whatever', False, None, None],

            # ping is never redirected
            ['http://127.0.0.1/ping', False, None, None],
            ['http://bazardelux.com/ping', False, None, None],
            ['http://www.bazardelux.com/ping', False, None, None],
            ['https://127.0.0.1/ping', False, None, None],
            ['https://bazardelux.com/ping', False, None, None],
            ['https://www.bazardelux.com/ping', False, None, None],

            # autocomplete is never redirected
            ['http://127.0.0.1/autocomplete.json', False, None, None],
            ['http://bazardelux.com/autocomplete.json', False, None, None],
            ['http://www.bazardelux.com/autocomplete.json', False, None, None],
            ['https://127.0.0.1/autocomplete.json', False, None, None],
            ['https://bazardelux.com/autocomplete.json', False, None, None],
            ['https://www.bazardelux.com/autocomplete.json', False, None, None],

            # And robots.txt?
            ['http://127.0.0.1/robots.txt', False, None, None],
            ['http://bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],
            ['http://www.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],
            ['http://sv.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],
            ['http://en.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],

            ['https://127.0.0.1/robots.txt', False, None, None],
            ['https://bazardelux.com/robots.txt', False, None, None],
            ['https://www.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],
            ['https://sv.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],
            ['https://en.bazardelux.com/robots.txt', True, 301, 'https://bazardelux.com/robots.txt'],

            # sitemap
            ['http://127.0.0.1/sitemap.xml', False, None, None],
            ['http://bazardelux.com/sitemap.xml', True, 301, 'https://bazardelux.com/sitemap.xml'],
            ['http://www.bazardelux.com/sitemap.xml', True, 301, 'https://bazardelux.com/sitemap.xml'],
            ['https://127.0.0.1/sitemap.xml', False, None, None],
            ['https://bazardelux.com/sitemap.xml', False, None, None],
            ['https://www.bazardelux.com/sitemap.xml', True, 301, 'https://bazardelux.com/sitemap.xml'],

            # Redirect http to https on page urls
            ['http://127.0.0.1/', False, None, None],
            ['http://bazardelux.com', True, 302, 'https://bazardelux.com/en'],
            ['http://bazardelux.com/', True, 302, 'https://bazardelux.com/en'],
            ['http://bazardelux.com/en', True, 302, 'https://bazardelux.com/en'],
            ['http://bazardelux.com/en/', True, 302, 'https://bazardelux.com/en'],
            ['http://bazardelux.com/sv', True, 302, 'https://bazardelux.com/sv'],
            ['http://bazardelux.com/sv/', True, 302, 'https://bazardelux.com/sv'],
            ['http://bazardelux.com/sv/blabla', True, 302, 'https://bazardelux.com/sv/blabla'],
            ['http://bazardelux.com/sv/blabla/', True, 302, 'https://bazardelux.com/sv/blabla'],
            ['http://www.bazardelux.com', True, 302, 'https://bazardelux.com/en'],
            ['http://www.bazardelux.com/', True, 302, 'https://bazardelux.com/en'],
            ['http://www.bazardelux.com/en', True, 302, 'https://bazardelux.com/en'],
            ['http://www.bazardelux.com/en/', True, 302, 'https://bazardelux.com/en'],
            ['http://www.bazardelux.com/sv', True, 302, 'https://bazardelux.com/sv'],
            ['http://www.bazardelux.com/sv/', True, 302, 'https://bazardelux.com/sv'],
            ['http://www.bazardelux.com/sv/blabla', True, 302, 'https://bazardelux.com/sv/blabla'],
            ['http://www.bazardelux.com/sv/blabla/', True, 302, 'https://bazardelux.com/sv/blabla'],
            ['https://127.0.0.1/', False, None, None],
            ['https://bazardelux.com', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com/', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com/en', False, None, None],
            ['https://bazardelux.com/en/', False, None, None],
            ['https://bazardelux.com/sv/blabla', False, None, None],
            ['https://bazardelux.com/sv/blabla/', False, None, None],
            ['https://www.bazardelux.com', True, 302, 'https://bazardelux.com/en'],
            ['https://www.bazardelux.com/', True, 302, 'https://bazardelux.com/en'],
            ['https://www.bazardelux.com/en', True, 302, 'https://bazardelux.com/en'],
            ['https://www.bazardelux.com/en/', True, 302, 'https://bazardelux.com/en'],
            ['https://www.bazardelux.com/sv/blabla', True, 302, 'https://bazardelux.com/sv/blabla'],
            ['https://www.bazardelux.com/sv/blabla/', True, 302, 'https://bazardelux.com/sv/blabla'],
        ]
        for url, does_redirect, redirect_code, redirect_url in tests:
            log.debug("Seeing if %s gets redirected" % url)
            m1.url = url
            m2.accept_languages = MagicMock()
            m2.accept_languages.values = MagicMock()
            m2.accept_languages.values.return_value = ['en-us', 'en_GB', 'sv']
            s.return_value = url.startswith('https:')
            if does_redirect:
                r.reset_mock()
                redirect_if_needed()
                r.assert_called_once_with(redirect_url, code=redirect_code)
            else:
                self.assertEqual(redirect_if_needed(), None, "%s not redirected" % url)


    @patch("www.localisation.request")
    @patch("www.redirect.request")
    @patch("www.redirect.redirect")
    @patch("www.redirect.is_https_request")
    def test_redirects_to_language(self, s, r, m1, m2):

        elbenv = 'awseb-e-6-AWSEBLoa-UJ1UCPBDE5KY-1623985950.eu-central-1.elb.amazonaws.com:443'

        tests = [
            # Url required, http Accept-Language, does redirect?, redirec code, redirect where
            ['https://bazardelux.com', 'sv,en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', True, 302, 'https://bazardelux.com/sv'],
            ['https://bazardelux.com/', 'en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com', 'en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com/', 'sv,en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', True, 302, 'https://bazardelux.com/sv'],
            ['https://bazardelux.com/sv', 'sv,en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', False, None, 'https://bazardelux.com/sv'],
            ['https://bazardelux.com/sv/', 'sv,en-US;q=0.8,en;q=0.6,lt;q=0.4,fr;q=0.2', False, None, 'https://bazardelux.com/sv'],

            ['https://bazardelux.com', 'en-us', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com/sv', 'en-us', False, None, 'https://bazardelux.com/sv'],

            ['https://bazardelux.com', '', True, 302, 'https://bazardelux.com/en'],
            ['https://bazardelux.com/sv', '', False, None, 'https://bazardelux.com/sv'],

            # And all those urls shouldn't be localized:
            ['https://bazardelux.com/ping', 'sv', False, None, ''],
            ['https://bazardelux.com/version', 'sv', False, None, ''],
            ['https://bazardelux.com/secured/version', 'sv', False, None, ''],
            ['https://bazardelux.com/chatfuel', 'sv', False, None, ''],
            ['https://bazardelux.com/v1', 'sv', False, None, ''],
            ['https://bazardelux.com/robots.txt', 'sv', False, None, ''],
            ['https://bazardelux.com/sitemap', 'sv', False, None, ''],

            # A live bug: infinite redirect loop...
            ['https://market-170314-2011-130.qqgmspnmtq.eu-central-1.elasticbeanstalk.com:443/secured/version', 'sv', False, None, ''],

            # And beanstalk env should be handled as bazardelux.com
            ['https://%s' % elbenv, '', True, 302, 'https://%s/en' % elbenv],
            ['https://%s/sv' % elbenv, 'sv', False, None, ''],
            ['https://%s/ping' % elbenv, 'sv', False, None, ''],

            # Legitimate paths don't get redirected
            ['https://bazardelux.com/sv/pris/JORDGLOB-Rath_SE_2016-11-16', '', False, None, None],
            ['https://bazardelux.com/en/price/JORDGLOB-Rath_SE_2016-11-16', '', False, None, None],
            ['https://bazardelux.com/sv/tillsalu/Michael-kors-klocka_1300_SEK__fb-1694779845', '', False, None, None],
            ['https://bazardelux.com/en/forsale/Michael-kors-klocka_1300_SEK__fb-1694779845', '', False, None, None],
        ]

        def accept_to_list(s):
            e1 = s.split(';')
            e2 = []
            for s in e1:
                e2 = e2 + s.split(',')
            return e2

        for url, accept_languages, does_redirect, redirect_code, redirect_url in tests:
            log.debug("Seeing if %s gets redirected" % url)
            m1.url = url
            m2.accept_languages = MagicMock()
            m2.accept_languages.values = MagicMock()
            m2.accept_languages.values.return_value = accept_to_list(accept_languages)

            s.return_value = url.startswith('https:')
            if does_redirect:
                r.reset_mock()
                redirect_if_needed()
                r.assert_called_once_with(redirect_url, code=redirect_code)
            else:
                self.assertEqual(redirect_if_needed(), None, "%s not redirected" % url)
