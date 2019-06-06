// Default share event logging. Should be overriden!
function log_share_event(data) {
    console.log("PLEASE OVERRIDE DEFAULT SHARE EVENT!!!");
}

// Log sharing events to localytics + append utm_source if needed
function my_addtoany_onshare(data) {
    console.log("Sharing! " + data.url + "  " + data.title + "  " + data.service);

    log_share_event(data);

    // If the target is facebook, append utm_source to the shared url
    old_url = data.url;
    new_url = old_url;

    if (old_url.indexOf('utm_source') === -1 ) {
        service = data.service.toLowerCase();
        if (service === 'facebook') {
            new_url = old_url + '?utm_source=facebook';
        } else if (service === 'email') {
            new_url = old_url + '?utm_source=email';
        }
    }

    // Modify the share by returning an object with a "url" property containing
    // the new URL
    if (new_url != old_url) {
        console.log("Changed share_url to " + new_url);
        return {
            url: new_url
        };
    }
}

// Configure sharing
var a2a_config = a2a_config || {};
a2a_config.linkname = '{{ a2a_title|safe }}';
a2a_config.linkurl = '{{ a2a_url|safe }}';
a2a_config.templates = {
    email: {
        subject: a2a_config.linkname,
        body: "{{ a2a_email_body|safe }}"
    }
};

a2a_config.callbacks = a2a_config.callbacks || [];
a2a_config.callbacks.push({
    share: my_addtoany_onshare
});
a2a.init('page');