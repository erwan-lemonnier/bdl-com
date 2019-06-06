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