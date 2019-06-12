import os
import logging
from uuid import uuid4
from unidecode import unidecode
from flask import Flask
from pymacaron import API, letsgo
from www.formats import get_custom_formats
from www.exceptions import bdl_error_reporter
from www.redirect import redirect_if_needed

from www.localisation import supported_languages, translate
from www.robots import serve_robots
from www.sitemap import serve_sitemap
from www.autocomplete import serve_autocomplete
from www.market import serve_market
from www.market import serve_market_tag
from www.market import serve_market_category
from www.market import serve_category_page


log = logging.getLogger(__name__)

app = Flask(__name__)


# Redirect to HTTPS, handle localisation and legacy urls
@app.before_request
def before_request():
    return redirect_if_needed()


# Set cache control headers
@app.after_request
def after_request(response):
    response.cache_control.max_age = 300
    response.headers.set('Content-Security-Policy', "child-src 'self' *.facebook.com *.facebook.net *.bazardelux.com *.hotjar.com *.wisepops.com *.localytics.com *.cloudfront.net *.googleapis.com *.google-analytics.com local.bazardelux.com:3000")
    return response


# -------------------------------------------------------------------------
#
# Plain HTML endpoints (the actual bazardelux web site)
#
# -------------------------------------------------------------------------

# Add endpoint, with and and without trailing slash
def publish(uri, method):
    log.info("Serving %s bound to %s" % (uri, method))
    app.add_url_rule(uri, str(uuid4()), method)
    if not uri.endswith('/'):
        log.info("Serving %s/ bound to %s" % (uri, method))
        app.add_url_rule(uri + '/', str(uuid4()), method)

# Root
publish('/', serve_market)
for l in supported_languages():
    publish('/%s' % l, serve_market)

# Market grid (landing page) and market announces
publish('/%s/<item_title>' % translate('URL_FORSALE_LABEL', 'en'), serve_market)
for l in supported_languages():
    market = unidecode(translate('URL_MARKET_LABEL', l))
    publish('/%s/%s' % (l, market), serve_market)
    for ll in supported_languages():
        # Support all combinations of language/forsale-label
        forsale = translate('URL_FORSALE_LABEL', ll)
        publish('/%s/%s/<item_title>' % (l, forsale), serve_market)

# Market tags
publish('/tag/<tag>', serve_market_tag)
for l in supported_languages():
    publish('/%s/tag/<tag>' % l, serve_market_tag)

# Market browsing categories
langs = ['/%s/' % l for l in supported_languages()]
langs.append('/')
for l in langs:
    publish('%sbrowse/<tag1>' % l, serve_market_category)
    publish('%sbrowse/<tag1>/<tag2>' % l, serve_market_category)
    publish('%sbrowse/<tag1>/<tag2>/<tag3>' % l, serve_market_category)
    publish('%sbrowse/<tag1>/<tag2>/<tag3>/<tag4>' % l, serve_market_category)
    publish('%sbrowse/<tag1>/<tag2>/<tag3>/<tag4>/<tag5>' % l, serve_market_category)
    publish('%sbrowse/<tag1>/<tag2>/<tag3>/<tag4>/<tag5>/<tag6>' % l, serve_market_category)

# Market categories
prefixes = ['/%s' % l for l in supported_languages()]
prefixes.append('/')
for s in prefixes:
    publish('%sfind/<cat1>' % s, serve_category_page)
    publish('%sfind/<cat1>/<cat2>' % s, serve_category_page)
    publish('%sfind/<cat1>/<cat2>/<cat3>' % s, serve_category_page)
    publish('%sfind/<cat1>/<cat2>/<cat3>/<cat4>' % s, serve_category_page)

# SEO
publish("/robots.txt", serve_robots)
publish("/sitemap.xml", serve_sitemap)
publish("/sitemap", serve_sitemap)


# -------------------------------------------------------------------------
#
# Autocomplete
#
# -------------------------------------------------------------------------

app.add_url_rule('/autocomplete.json', str(uuid4()), serve_autocomplete)
for l in supported_languages():
    app.add_url_rule('/%s/autocomplete.json' % l, str(uuid4()), serve_autocomplete)


def start(port=None, debug=None):

    here = os.path.dirname(os.path.realpath(__file__))
    path_apis = os.path.join(here, "apis")

    api = API(
        app,
        port=port,
        debug=debug,
        formats=get_custom_formats(),
        error_reporter=bdl_error_reporter,
    )
    api.load_apis(path_apis)
    api.publish_apis(path='docs')
    api.start(serve=['www'])


letsgo(__name__, callback=start)
