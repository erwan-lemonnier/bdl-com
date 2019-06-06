import logging
import re
import os
import json
from bs4.dammit import EntitySubstitution
from html.parser import HTMLParser
from flask import request
from babel.core import negotiate_locale


log = logging.getLogger(__name__)


esub = EntitySubstitution()
htmlparser = HTMLParser()


def supported_languages():
    return ['en', 'sv', 'fr']


TRANSLATIONS = {}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations.json')) as f:
    j = f.read()
    TRANSLATIONS = json.loads(j)


def html_to_unicode(s):
    """Take an html-encoded string and return a unicode string"""
    return htmlparser.unescape(s)


def unicode_to_html(s, keep_html=False):
    """Take a string containing non-ascii unicode characters and return
    properly encoded html"""
    s = esub.substitute_html(s)

    s = re.sub(re.compile('^[\s]+', re.MULTILINE), '', s)
    s = re.sub(re.compile('[\s]+$', re.MULTILINE), '', s)

    # Try to keep inline html or not. This is a sloppy method,
    # since text containing > and kept as html will endup messing
    # up the html of the page it is displayed in...
    if keep_html:
        s = s.replace('&lt;', '<')
        s = s.replace('&gt;', '>')
    else:
        s = s.replace('\n', '<br>')
        s = s.replace('\"', '&quot;')
        s = s.replace('\'', '&apos;')

    return s


def translate(name, language, default=None):
    name = name.upper()
    language = language.lower()
    if default:
        default = default.upper()
    if name in TRANSLATIONS:
        if language in TRANSLATIONS[name]:
            return TRANSLATIONS[name][language]
        else:
            return TRANSLATIONS[name]['en']
    elif default and default in TRANSLATIONS:
        if language in TRANSLATIONS[default]:
            return TRANSLATIONS[default][language]
        else:
            return TRANSLATIONS[default]['en']
    else:
        log.debug("MISSING TRANSLATION: %s %s" % (name, language))
        return ''


def get_page_language():
    """Try to infer the page's language, from the lang url argument first, else from the url"""

    # Do we have a ?lang= argument?
    if 'lang' in request.args:
        l = request.args['lang']
        if l in supported_languages():
            return l

    # Is there a language in the url?
    path = request.path
    if path and '/' in path:
        l = path.split('/')[1]
        if l in supported_languages():
            return l

    # Default to the user's prefered language
    return get_user_language()


def get_user_language():

    # An ugly hack to favoritize swedish speakers
    langs = str(request.accept_languages)
    log.info("User's Accept-Language are: %s" % langs)

    if 'sv' in langs:
        return 'sv'

    # Let's try to find a matching language
    languages = list(request.accept_languages.values())

    # Remove location part of locale
    for i in range(len(languages)):
        if '-' in languages[i]:
            languages[i] = languages[i].split('-')[0]
        elif '_' in languages[i]:
            languages[i] = languages[i].split('_')[0]

    # Defaults to babel's best match algorithm
    language = negotiate_locale(languages, supported_languages())
    if language:
        log.info("Babel identifies %s as user language [%s]" % (language, languages))
        return language

    log.info("Failed to find user's language from Accept-Languages [%s]. Defaulting to swedish" % languages)
    return 'sv'


def country_to_language(country):
    to_language = {
        'GB': 'en',
        'SE': 'sv',
        'UA': 'en',
        'FI': 'en',
    }

    if country in to_language:
        return to_language[country]

    return 'en'
