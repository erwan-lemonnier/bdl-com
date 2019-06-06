language = '{{ language|safe }}';
query_url = '{{ query_url|safe }}';
query_words = '{{ query_words|safe }}';

// Show a given category
function click_browse_link(category_name, category_url) {
    console.log("User clicked on category link " + category_name);

    log_click_link(
        'MarketBrowseCategory',
        {
            category: category_name,
            category_url: category_url,
            search_url: query_url
        }
    );

    location.href = category_url;
}

// Show the full item description on mobile
function click_see_more(item_uid, item_url) {
    console.log("User clicked on see more " + item_uid);

    log_click_link(
        'MarketShowItemSeeMore',
        {
            item_uid: item_uid,
            item_url: item_url,
            search_url: query_url
        }
    );

    dsc = $('#item-full-description-desktop').text();
    date = $('#item-description-date').text();
    $('#item-description-desktop').html(dsc);
    $('#item-description-desktop').append('<br/>');
    $('#item-description-desktop').append(date);

    dsc = $('#item-full-description-mobile').text();
    $('#item-description-mobile').html(dsc);

    return false;
}

// Show item announce (cert or imported data)
function item_click(item_uid, item_origin_url, item_url) {
    console.log("User clicked on Klue item " + item_uid);

    log_click_link(
        'MarketShowItem',
        {
            item_uid: item_uid,
            item_origin_url: item_origin_url,
            search_url: query_url
        }
    );

    // If mobile, open inline item view
    is_mobile = window.matchMedia("only screen and (max-width: 767px)").matches;
    if (is_mobile) {
        console.log("Redirecting to " + item_url);
        document.location=item_url;
        return false;
    }

    // else, show item as popup
    $.ajax({
        type: 'GET',
        url: '/v1/www/item/forsale/' + item_uid + '?lang=' + language,
		cache: false
    }).then(function(html) {
        // TODO: handle if response is an error
        console.log("Call to v1/www/item/forsale returns " + JSON.stringify(html, null, 4));
        $('#popup-container').html(html.html);

        console.log("Showing item popup");
        $.magnificPopup.open({
            items: {
                src: '#item-detail',
                type: 'inline'
            }
        });
    });
    return false;
}

// Preload next page
loaded_pages = {};

function preload_next_page() {
    ias = $.ias();
    url = ias.nextUrl;

    if (!(url in loaded_pages)) {
        loaded_pages[url] = 1

        console.log("Preloading url " + url);

        $.ajax({
            type: 'GET',
            url: url,
		    cache: false
        }).then(function(html) {
            // Extract picture urls from html
            count = 0;
            var $html = $(html);
            $('img', $html).replaceWith(function () {
                src = $(this).attr('src');
                new Image().src = src;
                count = count + 1;
            });
            console.log("Prefetched " + count + " images");
        });
    } else {
        console.log("Url " + url + " already preloaded.");
    }
}

// Show one item
function show_item(item, do_append) {
    console.log("Showing new item");

    // Make grid visible
    $('#pictures').show();

    // Make this item visible
    item.css({ opacity: 1, display: 'block' });
    h2s = item.find('h2');
    $(h2s).each(function() {
        $(this).css({ opacity: 1 });
    });
	item.show();
    if (do_append) {
        $('.grid').masonry('appended', item);
    }
}

//
// Code executed on page load
//

{% if focus_search %}
// Focus on search input
console.log("Focusing on search input");
$("#input-query-desktop").focus();
$("#input-query-mobile").focus();
{% endif %}

{% if item_html %}
// It's an item page, allow loading items without scroll
has_preloaded_items = true;
{% else %}
has_preloaded_items = false;
{% endif %}

// Setup infinite scroll with masonry
function show_items() {
    var $container = $('#pictures');

	$container.imagesLoaded(function(){
		$container.masonry({
	        itemSelector: '.grid-item',
            columnWidth: '.grid-sizer',
            percentPosition: true,
            gutter: 10
		});
	});
 	$container.imagesLoaded().progress(function(imgLoad, image) {
	    var $item = $( image.img ).parents('.grid-item');
        show_item($item, false);
    });
    $container.imagesLoaded().done(function(instance) {
        console.log('All images successfully loaded - Calling masonry/layout');
        $('.grid').masonry('layout');
    });

    var ias = $.ias({
        container: "#pictures",
        item: ".grid-item",
        pagination: "#pagination",
        next: ".next a",
        delay: 0,
        negativeMargin: 0,
    });

    // Block calling the next page until the user has actually scrolled down
    has_scrolled = false;
    ias.on('next', function(event) {
        if (has_scrolled == false && has_preloaded_items == false) {
            console.log("User has not scrolled down yet, and not an item page: blocking 'load' event and not fetching more items.");
            return false;
        }
        return true;
    });

    ias.on('scroll', function(offset, thres) {
        console.log("Scroll! " + offset + " " + thres);
        has_scrolled = true;
        preload_next_page();
    });

    ias.on('load', function(event) {
        console.log("Fetching " + event.url);
    });

    not_layed_out = true;
    ias.on('rendered', function(items) {
        console.log("Fetched new items...");

        // Make sure masonry/layout has been called once
        if (not_layed_out) {
            console.log("Calling masonry layout()");
            $('.grid').masonry('layout');
            not_layed_out = true;
        }

        // Show every item as its picture loads
        var $items = $(items);
        $('.grid').append($items);
 		$items.imagesLoaded().progress(function(imgLoad, image) {
	        var $item = $( image.img ).parents('.grid-item');
            show_item($item, true);
        });

        $container.imagesLoaded().done(function(instance) {
            console.log('All images successfully loaded - Calling masonry/layout');
            $('.grid').masonry('layout');
        });

        log_event(
            'MarketShowMoreScrollDown',
            {
                search_words: query_words,
                search_url: query_url
            }
        );
        console.log('Loaded ' + $items.length + ' items from server');
    });

    ias.on('noneLeft', function() {
        count = $('.grid-item').length;
        if (count == 0) {
            console.log('Found no items matching!');
            $('.no-items-found').show();
            $('.loading-spinner').hide();
        } else {
            console.log('No more items to fetch!');
            $('.no-more-items').show();
            $('.loading-spinner').hide();
        }
    });
}

$(document).ready(function() {
    show_items();
});

// Load the first page of results
log_event(
    'MarketShowFirstPage',
    {
        search_words: query_words,
        search_url: query_url
    }
);

{% if show_expert_controls %}

// Copied from http://www.the-art-of-web.com/javascript/getcookie/
function getCookie(name) {
    var re = new RegExp(name + "=([^;]+)");
    var value = re.exec(document.cookie);
    return (value != null) ? unescape(value[1]) : null;
}

function click_like_button(item_uid, origin_url, source, user_id) {
    console.log("User clicked expert-like button on p2p item: " + item_uid);

    log_click_button(
        'MarketItemExpertLike',
        {
            item_id: item_uid,
            origin_url: origin_url,
            source: source,
            user_id: user_id
        }
    );

    url = 'https://api-search.klue.it/v1/search/item/forsale/' + item_uid + '/like';
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify({'real': true, 'expert_id': user_id}, null, 4),
		cache: false,
        beforeSend: function (request) {
            var token = getCookie('token');
            request.setRequestHeader("Content-Type", 'application/json');
            request.setRequestHeader("Authorization", token);
        }
    }).then(function(ok) {
        // TODO: handle if response is an error
        console.log("Call to " + url + " returns "+ JSON.stringify(ok, null, 4));
        $.magnificPopup.close();
    });

    return false;
}

function click_delete_button(item_uid, origin_url, source, user_id) {
    console.log("User clicked expert-delete button on p2p item: " + item_uid);

    log_click_button(
        'MarketItemExpertDelete',
        {
            item_id: item_uid,
            origin_url: origin_url,
            source: source,
            user_id: user_id
        }
    );

    url = 'https://api-search.klue.it/v1/search/item/forsale/' + item_uid + '/archive';
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify({'real': true, 'reason': 'EXPERT_DELETE'}, null, 4),
		cache: false,
        beforeSend: function (request) {
            var token = getCookie('token');
            request.setRequestHeader("Content-Type", 'application/json');
            request.setRequestHeader("Authorization", token);
        }
    }).then(function(ok) {
        // TODO: handle if response is an error
        console.log("Call to " + url + " returns "+ JSON.stringify(ok, null, 4));
        $.magnificPopup.close();
    });

    return false;
}


function click_priority_button(item_uid, origin_url, source, user_id, level) {
    console.log("User clicked expert-prioritize button on item: " + item_uid + ". New level is " + level);

    log_click_button(
        'MarketItemExpertPrioritize',
        {
            item_id: item_uid,
            origin_url: origin_url,
            source: source,
            user_id: user_id
        }
    );

    url = 'https://api-search.klue.it/v1/search/item/forsale/' + item_uid + '/update';
    $.ajax({
        type: 'POST',
        url: url,
        data: JSON.stringify({'real': true, 'priority': level}, null, 4),
		cache: false,
        beforeSend: function (request) {
            var token = getCookie('token');
            request.setRequestHeader("Content-Type", 'application/json');
            request.setRequestHeader("Authorization", token);
        }
    }).then(function(ok) {
        // TODO: handle if response is an error
        console.log("Call to " + url + " returns "+ JSON.stringify(ok, null, 4));
        $.magnificPopup.close();
    });

    // Hide item in grid
    $("#" + item_uid).hide();

    return false;
}


function click_contact_seller_button(item_uid, origin_url, source, user_id) {
    alert("Not implemented yet!");
}

{% endif %}
