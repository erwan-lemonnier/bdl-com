log_event(
    'MarketShowItem',
    {
        item_id: '{{ item.uid|safe }}',
        url: '{{ item.url|safe }}',
    }
);

function log_share_event(data) {
    log_event(
        'MarketShareItem',
        {
            item_id: '{{ item.uid|safe }}',
            a2a_url: data.url,
            a2a_title: data.title,
            a2a_service: data.service
        }
    );
}

function click_buy_button(item_uid, origin_url, source, target) {
    console.log("User clicked buy button on p2p item: " + item_uid);
    log_item_click(item_uid, origin_url, source, target, 'MarketItemBuy');
    // Go directly to p2p announce, but in a separate tab if possible
    var win = window.open(origin_url, '_blank');
    win.focus();
    return false;
}

function click_messenger_button(item_uid, origin_url, source, target, goto_url) {
    console.log("User clicked contact expert on p2p item: " + item_uid);
    log_item_click(item_uid, origin_url, source, target, 'MarketItemContactExpert');
    var win = window.open(goto_url, '_blank');
    win.focus();
    console.log("returning false");
    return false;
}

function click_sell_info_button(item_uid, origin_url, source, target, goto_url) {
    console.log("User clicked sell on kluemarket on p2p item: " + item_uid);
    log_item_click(item_uid, origin_url, source, target, 'MarketItemSellInfo');
    document.location=goto_url;
    return false;
}

function log_item_click(item_uid, origin_url, source, target, name) {
    log_click_button(
        name,
        {
            item_id: item_uid,
            origin_url: origin_url,
            source: source,
            target: target,
        }
    );
}

{% if cert_id %}
// Setup certificate slideshow
jQuery(document).ready(function() {
    // Initialize definition popup
    console.log("Initializing magnificPopup");
    $('.open-popup-link').magnificPopup({
        type:'ajax',
        midClick: true
    });

    is_mobile = window.matchMedia("only screen and (max-width: 767px)").matches;

    if (is_mobile) {
        slider_id = '#lightSlider-{{ cert_id|safe }}-mobile';
    } else {
        slider_id = '#lightSlider-{{ cert_id|safe }}-desktop';
    }

    console.log("Initializing slider " + slider_id);
    slider = $(slider_id).lightSlider({
        gallery: false,
        item: 1,
        loop: true,
        slideMargin: 0,
        thumbItem: 6,
        adaptiveHeight: true,
        keyPress: true,
        enableTouch: true,
        enableDrag: true,
        onSliderLoad: function() {
            // Refreshing after loads fixes the bug/issue of the first image
            // disappearing after load
            {% if is_popup %}
            console.log("Refreshing slider");
            slider.refresh();
            {% endif %}
        }
    });

    // Make slider visible
    $(slider_id).css({'display': 'block'});

    $('.lSSlideOuter ul').css("margin", '0 auto');
    $('.lSSlideOuter ul').css("margin-top", '0.5em');
});

// Localytics
log_event(
    'CertificateShow',
    {
        cert_id: '{{ cert_id|safe }}',
        cert_url: '{{ cert_url|safe }}',
        language: '{{ cert_language|safe }}',
        age_days: '{{ cert_age|safe }}',
        cert_version: '{{ cert_version|safe }}',
    }
);
{% endif %}