function click_menu(link_name, url) {
    log_click_link('Menu' + link_name, url);
    log_click_link('Menu', url);
    document.location=url;
    return false;
}

function focus_search(language) {
    // Are we showing the market page?
    i = $('#input-query-desktop');
    if (i.length == 0) {
        // This is not the market view: open it!
        console.log("Opening market view");
        document.location='https://bazardelux.com?focus=1';
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
        words = $('#input-query-mobile').val();
        console.log("Searchbox mobile contains words [" + words + "]");
    } else {
        words = $('#input-query-desktop').val();
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

// Setup autocomplete
function setup_autocomplete( request, response ) {
    url = "/autocomplete.json";
    $.getJSON("/autocomplete.json", function( data ) {
        console.log("Fetched autocomplete json");
        $( "#input-query-mobile" ).autocomplete({
            source: data['words'],
            preventBadQueries: false,
            open: function(event, ui) {
                $('.ui-autocomplete').off('menufocus hover mouseover mouseenter');
            }
        });
        $( "#input-query-desktop" ).autocomplete({
            source: data['words'],
            preventBadQueries: false,
            open: function(event, ui) {
                $('.ui-autocomplete').off('menufocus hover mouseover mouseenter');
            }
        });
    });
}

$(document).ready(function(){
    // Toggle animation of hamburger icon
	$('#nav-icon3').click(function(){
		$('#nav-icon3').toggleClass('open');
        $('#nav-tray').toggleClass('nav-tray-hide').toggleClass('nav-tray-show');

        if ($('#nav-icon3').hasClass('open')) {
            // Set height of the nav-tray: 100% height - top menu - nav links height
            h = window.innerHeight - 55 - 400 + 8;
            if (h < 0) {
                h = 0;
            }
            $('.nav-tray-show').css({'padding-bottom': h});
            console.log("Setting nav-tray padding to " + h);
        } else {
            $('.nav-tray-show').css({'padding-bottom': 0});
            $('.nav-tray-hide').css({'padding-bottom': 0});
        }

	});

    // Hide/unhide search form on mobile
	$('#icon-search-menu').click(function(){
        console.log("toggle search mobile");
		$('#icon-search-menu').toggleClass('icon-hide');
		$('#search-tray').toggleClass('search-tray-hide').toggleClass('search-tray-show');
	});

    // Capture search events on mobile
    $("#input-query-mobile").keyup(function (e) {
        if (e.which == 13) {
            do_search('{{ language|safe }}');
        }
    });
    $("#input-query-desktop").keyup(function (e) {
        if (e.which == 13) {
            do_search('{{ language|safe }}');
        }
    });

    // Configure autocompletion
    setup_autocomplete();
});

$(function() {
    $('.footer-select-language').on('change', function(){
        var newurl = $(this).find("option:selected").attr('value');
        log_click_button('PickLanguage')
        console.info("Redirecting to " + newurl)
        document.location=newurl;
    });
});

function click_footer(link_name, url) {
    log_click_link('Footer' + link_name, url);
    log_click_link('Footer', url);
    document.location=url;
    return false;
}
