import logging
import re
import os
import difflib
from pymacaron.test import PyMacaronTestCase


log = logging.getLogger(__name__)


class Test(PyMacaronTestCase):

    def normalize_html(self, s):
        s = re.sub("age_days: '\d+',", "age_days: '666',", s)
        if '</result>' in s:
            a, b = s.split('<result', 1)
            tail = b.split('</result>')
            s = '%s\n</results>%s' % (a, tail[-1])
        s = re.sub('http://127.0.0.1:8080', 'https://kluemarket.com', s)
        return s


    def load_file(self, path):
        p = os.path.join(os.path.dirname(__file__), 'pages', path)
        with open(p, 'r') as f:
            s = f.read()
        return self.normalize_html(s)


    def cleanup_html(self, p):
        lines = []
        for l in p.split('\n'):
            l = l.strip()
            if len(l):
                lines.append(l)
        return '\n'.join(lines)


    def show_html_diff(self, a, b):
        aa = a.splitlines(1)
        bb = b.splitlines(1)

        diff = difflib.unified_diff(aa, bb)
        print("diff:\n" + ''.join(diff))


    def assertSameHTML(self, p1, p2):
        p1 = self.cleanup_html(p1)
        p2 = self.cleanup_html(p2)
        self.show_html_diff(p1, p2)
        self.assertEqual(p1, p2)


    def assertSamePages(self, file, url, token=None):
        html = self.load_file(file)
        auth = None
        if token:
            auth = 'Bearer %s' % token

        page = self.assertCallReturnHtml(
            'GET',
            url,
            auth=auth,
        )
        page = self.normalize_html(page)
        self.assertSameHTML(html, page)
