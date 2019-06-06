import logging
import re
from flask import redirect, request
from www.localisation import supported_languages


log = logging.getLogger(__name__)


def redirect_if_needed():
    """Redirect *.bazardelux.com to bazardelux.com when needed +
    redirect http to https except for pings"""

    url = request.url

    domain = url.split('//')[1].split('/')[0]
    extension = domain.split('.')[-1]
    # uri = '/'.join(url.split('//')[1].split('/')[1:])

    # Assume we should redirect to kluemarket.com, except if it's a temporary
    # beanstalk environment during deployment
    target_domain = 'bazardelux.com'
    if 'eu-west-1.elb.amazonaws.com' in domain or 'eu-west-1.elasticbeanstalk.com' in domain:
        target_domain = domain

    log.info("URL requested is %s (domain:%s ext:%s)" % (url, domain, extension))

    # Is it a virtualbox container or a dev process?
    if re.match(r'^[0-9\.]+$', domain) or domain == 'localhost' or ':8080' in url:
        log.info("Not redirecting to SSL: this is a dev container or process (%s)" % url)
        return

    #
    # Special urls: ping, robots, sitemap, autocomplete.json
    #

    if '/v1/' in url:
        # It's an api call. Pass it through, but make sure it gets https
        log.info("It's an api call")
        return

    if url.endswith('/autocomplete.json'):
        # Don't redirect autocomplete
        log.info("Fetching autocomplete: not redirecting it (%s)" % url)
        return

    if url.endswith('/service-worker.js') or '/static/' in url or url.endswith('/favicon.ico'):
        # Serving react files: don't redirect
        log.info("Fetching react file: not redirecting it (%s)" % url)
        return

    if url.endswith('/ping'):
        # Don't redirect pings (else elasticbean would assume instance is dead)
        log.info("It's a ping url: not redirecting it (%s)" % url)
        return

    if url.endswith('/robots.txt'):
        if not is_https_request():
            log.info("Redirecting robots.txt to https for %s" % url)
            return redirect('https://%s/robots.txt' % target_domain, code=301)
        elif domain != target_domain:
            log.info("Redirecting %s to %s" % (domain, target_domain))
            return redirect('https://%s/robots.txt' % target_domain, code=301)
        else:
            log.info("Not redirecting robots.txt url %s" % url)
            return

    if url.endswith('/sitemap.xml') or url.endswith('/sitemap'):
        if not is_https_request():
            extension = url.split('//')[1].split('/')[0].split('.')[-1]
            log.info("Redirecting sitemap to https for %s" % url)
            return redirect('https://%s/sitemap.xml' % target_domain, code=301)
        elif domain != target_domain:
            log.info("Redirecting %s to %s" % (domain, target_domain))
            return redirect('https://%s/sitemap.xml' % target_domain, code=301)
        else:
            return

    #
    # All other urls
    #

    do_redirect = False

    # Remove www. and redirect lang.bazardelux.com to bazardelux.com/lang
    from_to = {
        '//www.bazardelux': '//bazardelux',
    }
    for l in supported_languages():
        from_to['//%s.%s/' % (l, target_domain)] = '//%s/%s' % (target_domain, l)

    for k, v in from_to.items():
        if k in url:
            log.info("Replacing '%s' with '%s'" % (k, v))
            url = url.replace(k, v, 1)
            do_redirect = True

    url = url.rstrip('/')

    # Redirect http to https
    if not is_https_request():
        do_redirect = True

    # Should we redirect the user to a specific language?
    pattern = re.compile('%s/(_test|auth|robots|doc|apidoc|sitemap|version|secured|ping|v1|chatfuel|%s)' % (target_domain, '|'.join(supported_languages())))
    if re.search(pattern, url):
        log.info("Url is already localized or should not be localized")
    else:
        log.info("Url is not localized and should be")
        # language = get_user_language()
        language = 'sv'
        url = url.replace(target_domain, '%s/%s' % (target_domain, language))
        log.info("User prefers language %s. Redirecting to %s" % (language, url))
        do_redirect = True

    if do_redirect:
        # Make sure we redirect to https, to avoid ping-pong loop between http and https
        url = url.replace('http:', 'https:')
        log.info("Redirecting to '%s'" % url)
        return redirect(url, code=302)


def is_https_request():
    """Find out if the original request came over https (true) or just http
    (false)"""

    log.info("is_https_request: Got request url: %s" % request.url)
    log.info("is_https_request: Got request headers: %s" % request.headers)

    if 'X-Forwarded-Proto' in request.headers:
        if request.headers.get('X-Forwarded-Proto', '').lower() == 'https':
            log.debug("Called over https, according to X-Forwarded-Proto")
            return True
        else:
            log.debug("Called over http, according to X-Forwarded-Proto")
            return False

    if 'https' in request.url.lower():
        log.debug("Called over https, according to url (%s)" % request.url)
        return True

    log.debug("Request was made over http (url:%s) (X-Forwarded-Proto:%s)" % (request.url, request.headers.get('X-Forwarded-Proto', '')))
    return False
