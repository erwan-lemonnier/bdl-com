function click_menu(link_name, url) {
    log_click_link('Menu' + link_name, url);
    log_click_link('Menu', url);
    document.location=url;
    return false;
}

function focus_search(language) {
    // Are we showing the market page?
    i = $('#input-query-header');
    if (i.length == 0) {
        // This is not the market view: open it!
        console.log("Opening market view");
        document.location='https://kluemarket.com?focus=1';
    } else {
        // We are on the market page already: focus on input
        console.log("Focusing on search input");
        $('html,body').animate({scrollTop: i.offset().top - 60}, 200, function() {
            i.focus();
        });
    }
}

// Call the search API
function do_search(language) {

    is_mobile = window.matchMedia("only screen and (max-width: 767px)").matches;

    if (is_mobile) {
        words = $('#input-query-header').val();
        console.log("Searchbox mobile contains words [" + words + "]");
    } else {
        words = $('#input-query').val();
        console.log("Searchbox desktop contains words [" + words + "]");
    }

    if (words == null || words.length == 0) {
        words = '*'
    }

    log_click_button(
        'MarketNewSearch',
        {
            search_words: words
        }
    );

    url = '{{ search_url }}?query=' + encodeURIComponent(words);
    console.log("Calling " + url);
    location.href = url;
}
