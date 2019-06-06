import logging
from flask import jsonify
# from bdl.s3 import get_s3_conn
from pymacaron.crash import crash_handler
from www.localisation import html_to_unicode


log = logging.getLogger(__name__)


WORDS = []

# for name in ('design-whitelist.html', 'mode-whitelist.html'):
#     log.info("Fetching list %s from S3" % name)
#     k = get_s3_conn().get_bucket('static.bazardelux.com').get_key('crawler/' + name)
#     s = k.get_contents_as_string().decode('utf-8')
#     lst = [l.strip() for l in s.split('\n') if len(l.strip()) > 0]
#     lst = [html_to_unicode(l).lower() for l in lst]
#     WORDS = WORDS + lst

@crash_handler
def serve_autocomplete():
    return jsonify(words=WORDS)
