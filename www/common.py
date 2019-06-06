import logging
from flask import request
from pymacaron.auth import generate_token
from www.localisation import supported_languages
from www.localisation import unicode_to_html
from www.localisation import translate


log = logging.getLogger(__name__)


def get_domain(language=None):
    if not language:
        return 'bazardelux.com'
    return 'bazardelux.com/%s' % language


def get_base_url(language=None):
    if '192.168.56.102:8080' in request.url:
        u = 'http://192.168.56.102:8080'
        if language:
            u = '%s/%s' % (u, language)
        return u
    return 'https://%s' % get_domain(language=language)


def generate_hreflangs(current_language, callback_patch_url):
    d = {
        'hreflangs': [],
        'hreflinks': '',
    }
    for l in supported_languages():
        name = unicode_to_html(translate('LANG_%s' % l.upper(), l, default='LANG_EN'))
        url = callback_patch_url(l)
        d['hreflangs'].append({
            'name': name,
            'lang': l,
            'url': url,
            'selected': current_language == l,
        })
        cls = 'class="footer-lang-not-selected item-not-active"'
        if current_language == l:
            cls = 'class="footer-lang-selected item-active"'
        d['hreflinks'] = '%s | %s' % (d['hreflinks'], '<a href="%s" %s>%s</a>' % (url, cls, name))

    d['hreflinks'] = d['hreflinks'].strip().strip('|').strip(' ')

    return d
