import logging
from flask import redirect
from pymacaron.crash import crash_handler


log = logging.getLogger(__name__)


@crash_handler
def serve_sitemap():
    """Serve sitemap for the search service"""

    map_url = "https://static.baxardelux.com/sitemap-www-https-bazardelux-com.xml"
    log.info("Redirecting to %s" % (map_url))
    return redirect(map_url, code=301)
