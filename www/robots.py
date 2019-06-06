import logging
from flask import Response
from pymacaron.crash import crash_handler


log = logging.getLogger(__name__)


@crash_handler
def serve_robots():
    """Serve robots for the search service"""
    robots = '\n'.join([
        'User-Agent: *',
        'Sitemap: https://bazardelux.com/sitemap.xml',
        'Disallow: /v1/',
        'Disallow: /version',
        'Disallow: /secured/version',
        'Disallow: /ping',
        ''
    ])
    log.info("Returning '%s'" % robots)
    return Response(robots, mimetype='text/plain')
