function toggle_menu() {
    console.log("Toggling menu");
    var x = document.getElementById("menu-nav-links");
    if (x.className === "menu-nav-collapse") {
        x.className += " responsive";
    } else {
        x.className = "menu-nav-collapse";
    }
    log_click_button('MenuExpand');
}

function click_menu(link_name, url) {
    log_click_link('Menu' + link_name, url);
    log_click_link('Menu', url);
    document.location=url;
    return false;
}

function click_menu_new_tab(link_name, url) {
    // Open url in new tab (or new window)
    log_click_link('Menu' + link_name, url);
    log_click_link('Menu', url);
    win = window.open(url, '_blank');
    win.focus();
    return false;
}