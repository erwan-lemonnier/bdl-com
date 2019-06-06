
function log_page_view() {
    page_name = '{{ page_name }}';
    console.log("Logging page view: " + page_name);

    /* Google Analytics */
    ga('set', 'page', page_name);
    ga('set', 'ul', '{{ language|safe }}');

    ga(
        'send',
        {
            hitType: 'pageview',
        }
    );

    /* Mixpanel */
    mixpanel.track(page_name);

    /* Localytics */
    ll('tagScreen', page_name);

    /* Facebook */
    fbq('track', 'ViewContent');

    /* Events */
    log_event('ViewPage' + page_name);
    log_event('ViewPage');
}

function log_click_link(link_name, url) {
    log_event(
        'Link' + link_name,
        {
            to_url: url
        }
    );
}

function log_click_button(button_name, more_tags) {
    log_event(
        'Btn' + button_name,
        more_tags
    );
}

function log_event(event_name, more_tags) {
    event_category = 'Event';
    event_action = 'none';
    if (event_name.indexOf('Link') == 0) {
        event_category = 'Link';
        event_action = 'click';
    } else if (event_name.indexOf('Btn') == 0) {
        event_category = 'Button';
        event_action = 'click';
    } else if (event_name.indexOf('View') == 0) {
        event_category = 'PageView';
    } else if (event_name.indexOf('Event') != 0) {
        event_name = 'Event' + event_name;
    }

    tags = {
        referrer: '{{ referrer|safe }}',
        language: '{{ language|safe }}',
        backend_version: '{{ backend_version|safe }}',
        klue_domain: 'kluemarket.com',
        page_name: '{{ page_name }}'
    };

    if (more_tags) {
        for (var attrname in more_tags) {
            tags[attrname] = more_tags[attrname];
        }
    }

    if (!('url' in tags)) {
        tags['url'] = [location.host, location.pathname].join('');
    }

    console.log("Logging analytics event " + event_name + ": " + JSON.stringify(tags, null, 4));

    ll(
        'tagEvent',
        event_name,
        tags
    );

    ga(
        'event',
        {
            hitType: 'event',
            eventCategory: event_category,
            eventAction: event_action,
            eventLabel: event_name,
        }
    );

    mixpanel.track(
        event_name,
        tags
    );
}
