import logging
from unidecode import unidecode
from www.localisation import unicode_to_html, translate
from www.common import get_base_url
from www.common import generate_hreflangs


log = logging.getLogger(__name__)


def get_menu_data(language, patch_url=None, whitefooter=False, search_url=None):
    data = get_menu_translations(language)

    if search_url:
        data['search_url'] = search_url

    if patch_url:
        hreflangs = generate_hreflangs(language, patch_url)
        data.update(hreflangs)

    # The mobile popdown part
    data['menu_nav'] = get_footer_data(language)
    data['menu_nav'].insert(0, {
        'name': 'Sell',
        'label': unicode_to_html(translate('MENU3_SELL_LABEL', language)),
        'url': '%s/sell' % get_base_url(language=language),
        'active': False,
    })

    data['menu_nav'].insert(2, {
        'name': 'PriceDB',
        'label': unicode_to_html(translate('MENU3_PRICEDB_LABEL', language)),
        'url': '%s/%s' % (get_base_url(language=language), unidecode(translate('MENU3_PRICEDB', language))),
        'active': False,
    })

    data['language'] = language

    # Backward compatibility: remove once all pages use menu_nav instead of footer_data
    data['footer_data'] = get_footer_data(language)
    data['whitefooter'] = whitefooter

    return data


def get_menu_translations(language):
    menu_data = {
        'url_menu_base': get_base_url(language=language),

        'label_free_appraisal': unicode_to_html(translate('MENU2_FREE_APPRAISAL_LABEL', language)),

        'label_link_market': 'Market',
        'url_link_market': get_base_url(language=language),

        'url_link_home': get_base_url(language=language),
        'url_link_about': '%s/about' % get_base_url(language=language),

        'label_sell_something': unicode_to_html(translate('MENU2_SELL_SOMETHING', language)),
        'url_sell_something': 'https://m.me/kluemarket?ref=Welcome%20message',

        'label_link_sell_old': unicode_to_html(translate('MENU2_LABEL_ABOUT', language)),

        'label_link_valuation': unicode_to_html(translate('MENU2_APPRAISAL_LABEL', language)),
        'url_link_valuation': '%s/about' % get_base_url(language=language),

        'label_link_certificate': unicode_to_html(translate('MENU2_CERTIFICATE_LABEL', language)),
        'url_link_certificate': '%s/about#iphoneapp' % get_base_url(language=language),

        'url_link_pricedb': '%s/%s' % (get_base_url(language=language), translate('MENU2_PRICEDB', language)),
        'label_link_pricedb': unicode_to_html(translate('MENU2_PRICEDB_LABEL', language)),

        'label_link_sell': unicode_to_html(translate('MENU2_SELL_LABEL', language)),

        'url_link_messenger': 'https://m.me/kluemarket?ref=Welcome%20message',

        'label_search_placeholder': unicode_to_html(translate('MARKET_SEARCH_PLACEHOLDER', language)),

        'search_url': get_base_url(language=language),

        'show_search_tray': False,
    }

    menu_data['url_link_sell'] = 'https://www.klue.se'
    if language != 'sv':
        menu_data['url_link_sell'] = 'https://www.klue.se/en'

    menu_data['url_link_logo'] = menu_data['url_link_sell']

    return menu_data


def get_footer_data(language):
    return [
        {
            'name': 'Faq',
            'label': 'FAQ',
            'url': '%s/faq' % get_base_url(language=language),
            'active': False,
        },
        {
            'name': 'Blog',
            'label': 'Blog',
            'url': 'https://blog.kluemarket.com',
            'active': False,
        },
        {
            'name': 'About',
            'label': unicode_to_html(translate('FOOTER_LABEL_ABOUT', language)),
            'url': '%s/about' % get_base_url(language=language),
            'active': False,
        },
    ]
