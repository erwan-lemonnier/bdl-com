import logging
from urllib.parse import quote_plus, urlencode
import re
from flask import request, render_template, make_response
from unidecode import unidecode
from pymacaron.auth import authenticate_http_request, backend_token
from pymacaron.crash import crash_handler, report_error
from pymacaron.exceptions import is_error
from pymacaron.config import get_config
from pymacaron_core.swagger.apipool import ApiPool
# from pnt_common.rest import user_is_expert, user_is_admin, get_userid
from www.menu import get_menu_data, get_menu_translations
from www.localisation import get_page_language
from www.localisation import unicode_to_html
from www.localisation import html_to_unicode
from www.localisation import translate
from www.localisation import country_to_language
from www.common import get_base_url


log = logging.getLogger(__name__)


def get_search_url(language=None, params=None, category_tag=None):
    """Given url parameters (already encoded) and an optional category tag, return
    the search url to show the same results"""

    category_uri = ''
    if category_tag:
        category_uri = category_tag.replace(':path:', '/browse/').replace(':', '/')
        category_uri = category_uri.rstrip('/')

    search_url = '%s%s' % (get_base_url(language), category_uri)

    if params:
        search_url = '%s?%s' % (search_url, params)

    return search_url


def extract_item_uid(item_title):
    log.debug("Checking if [%s] contains a valid item_uid" % item_title)
    if '__' not in item_title:
        return None
    uid = item_title.split('__', 1)[1]
    for c in ('.', ',', '?', '#', ':', ';', '\'', '&'):
        if c in uid:
            uid = uid.split(c)[0]
    if re.match('^(tr|fb|kl|bl|wtf)-[0-9a-z]{6}([0-9a-z]{4}[0-9a-z]*)?$', uid):
        return uid
    return None


def normalize_item_for_sale(item, language=None):
    item.bdlitem.title = unicode_to_html(item.bdlitem.title)
    item.bdlitem.description = unicode_to_html(item.bdlitem.description)

    if not item.count_views:
        item.count_views = 0

    item.url = gen_item_forsale_url(item, language=language)

    display_prio_to_prio = {
        10: 'high',
        3: 'medium',
        2: 'medium',
        1: 'normal',
        0: 'low',
    }

    if item.display_priority is not None:
        item.prio = display_prio_to_prio[item.display_priority]
    else:
        item.prio = 'normal'


def get_item_forsale(item_uid):
    """Get an item forsale, even if it has been archived"""
    item = None
    with backend_token() as token:
        log.info("Trying to get %s from index of items forsale" % item_uid)
        item = ApiPool.api.client.get_item(
            id=item_uid,
            request_headers={
                'Authorization': 'Bearer %s' % token,
            }
        )

        if is_error(item):
            report_error("Failed to fetch item %s" % (item_uid), caught=item)
            return None

    return item


def item_forsale_to_html(item, language, is_popup=True):
    """Return the html of the item popup"""

    normalize_item_for_sale(item, language=language)

    item.description = re.sub('<[bB][rR]>', ' ', item.description)
    item.short_description = item.description[0:180]

    #
    # A copied p2p announce
    #

    email_body = '%s\n%s' % (item.description, item.url)
    email_body = email_body.replace('\n', '\\n')

    # Else, default to showing non-certificate item popup
    location = translate('COUNTRY_%s' % item.bdlitem.country.upper(), language)
    if item.facebook_location:
        location = item.facebook_location
    if item.blocket_location:
        location = item.blocket_location

    item_location_query = urlencode({'q': unicode_to_html(location.replace(',', ''))})

    log.info("Item is from %s" % item.source)

    #
    # Format buy button label
    #

    cur = item.currency.lower()
    src = ''
    log.info("ITEM IS %s" % item)
    if cur == 'sek':
        cur = 'kr'
    if item.source == 'facebook':
        src = unicode_to_html(translate('MARKET_LABEL_ON_FACEBOOK', language))
    elif item.source == 'blocket':
        src = unicode_to_html(translate('MARKET_LABEL_ON_BLOCKET', language))
    elif item.source == 'tradera':
        src = unicode_to_html(translate('MARKET_LABEL_ON_TRADERA', language))

    label_buy_button = '%s %s %s' % (item.price, cur, src)

    # Set the item.source_details, used for analytics purpose. More specific than .source
    item.source_details = item.source
    if item.source == 'facebook':
        item.source_details = item.facebook_group_id

    itemdata = {
        'is_popup': is_popup,
        'cert_id': cert_id,
        'item': item,
        'language': language,
        'label_not_reviewed': unicode_to_html(translate('MARKET_LABEL_NOT_EXPERT_REVIEWED', language), keep_html=True),
        'label_is_certified': unicode_to_html(translate('MARKET_LABEL_IS_CERTIFIED', language), keep_html=True),
        'label_is_reviewed': unicode_to_html(translate('MARKET_LABEL_IS_EXPERT_REVIEWED', language), keep_html=True),
        'label_date': unicode_to_html(translate('MARKET_LABEL_DATE', language)),
        'label_in_location': unicode_to_html(translate('MARKET_LABEL_IN_LOCATION', language)),
        'label_expert_only': unicode_to_html(translate('MARKET_EXPERT_ONLY', language)),
        'item_location': unicode_to_html(location),
        'label_buy_button': label_buy_button,
        'label_sold_button': unicode_to_html(translate('MARKET_LABEL_ITEM_SOLD', language)),
        'google_maps_api_key': get_config().google_maps_api_key,
        'item_location_query': item_location_query,
        'a2a_title': item.title,
        'a2a_url': item.url,
        'a2a_email_body': email_body,
        'label_how_klue_works': unicode_to_html(translate('MARKET_LABEL_HOW_KLUE_WORKS', language)),
        'user_id': get_userid(),
        'show_expert_controls': expert_controls,
        'read_more_label': unicode_to_html(translate('MARKET_LABEL_SEE_MORE', language), keep_html=True),
        'label_also_for_sale': unicode_to_html(translate('MARKET_ALSO_FOR_SALE', language)),

        'label_bullet_messenger': unicode_to_html(translate('MARKET_BULLET_MESSENGER', language)),
        'label_bullet_sell': unicode_to_html(translate('MARKET_BULLET_SELL', language)),
        'label_bullet_see_more': unicode_to_html(translate('MARKET_BULLET_SEE_MORE', language), keep_html=True),
        'url_bullet_messenger': '%s/messenger' % get_base_url(language),
        'url_bullet_sell': '%s/sell' % get_base_url(language),

        'label_bullet_certified': unicode_to_html(translate('MARKET_BULLET_CERTIFIED', language), keep_html=True),
    }

    itemdata.update(get_menu_translations(language))

    return render_template(
        'market2/itemdetail.html',
        **itemdata
    )


@crash_handler
def serve_market_tag(tag):
    """Return the market grid and let it populate itself with search results"""
    tag = tag.replace('_', ' ')
    query_words = ':%s:' % tag
    return serve_market_page(query_words)


@crash_handler
def serve_market_category(tag1, tag2=None, tag3=None, tag4=None, tag5=None, tag6=None):
    """Return the market grid set to a given category"""
    query_words = request.args.get('query', '')

    category = ':path'
    for t in (tag1, tag2, tag3, tag4, tag5, tag6):
        if t:
            category = '%s:%s' % (category, t)
    category = category + ':'

    return serve_market_page(query_words, category_tag=category)


@crash_handler
def serve_market(item_title=None):
    """Return the market grid and let it popuplate itself with search results"""
    query_words = request.args.get('query', '')
    return serve_market_page(query_words, item_title)


def get_category_path_data(category_tag, language):
    """Return data used in templates to visualize item/page path"""
    assert category_tag
    assert language

    data = []

    data.append({
        'name': 'all',
        'label': unicode_to_html(translate('CATEGORY_ALL', language)),
        'url': get_base_url(language),
        'last': False,
    })

    path = ''
    for name in category_tag.replace(':path:', '').rstrip(':').split(':'):
        if name == '':
            continue
        path = '/'.join([path, name])

        d = {
            'name': name,
            'label': unicode_to_html(translate('CATEGORY_%s' % name.upper(), language)),
            'url': '%s/browse%s' % (get_base_url(language), path),
            'last': False,
        }

        # If not translation found, use the name
        if 'CATEGORY_' in d['label']:
            d['label'] = name.title()

        data.append(d)

    data[-1]['last'] = True

    # log.debug("Tag %s gives path data: %s" % (category_tag, json.dumps(data, indent=4)))

    return data


def serve_market_page(query_words, item_title=None, category_tag=None):

    item_uid = None
    if item_title:
        item_uid = extract_item_uid(item_title)
        log.info("Found item_uid=%s" % item_uid)

    language = get_page_language()
    country = None
    page = 0

    # Extract query arguments
    if 'lang' in request.args:
        language = request.args.get('lang', 'en')

    if 'page' in request.args:
        page = int(request.args.get('page', '0'))

    if 'country' in request.args:
        country = request.args.get('country', 'SE')

    latest = False
    if 'latest' in request.args:
        if str(request.args.get('latest', '')).lower() in ('1', 'true'):
            latest = True

    curated = None
    if 'curated' in request.args:
        if str(request.args.get('curated', '')).lower() in ('1', 'true'):
            curated = True
        elif str(request.args.get('curated', '')).lower() in ('0', 'false'):
            curated = False

    focus_search = False
    if 'focus' in request.args:
        focus_search = True

    log.info("Got query for words [%s]" % query_words)

    html_page_title = generate_title('MARKET_PAGE_TITLE', language)
    header_title_line1 = unicode_to_html(translate('MARKET_HEADER_LINE1', language), keep_html=True)
    header_title_line2 = unicode_to_html(translate('MARKET_HEADER_LINE2', language), keep_html=True)
    page_description = unicode_to_html(translate('MARKET_PAGE_DESCRIPTION', language))
    meta_description = page_description
    market_button_label = unicode_to_html(translate('MARKET_SEARCH_BUTTON_LABEL', language))
    market_input_placeholder = unicode_to_html(translate('MARKET_SEARCH_PLACEHOLDER', language))
    label_end_reached = unicode_to_html(translate('MARKET_LABEL_END_REACHED', language))
    label_no_items_found = unicode_to_html(translate('MARKET_NO_HITS', language))

    if query_words == '':
        market_input_value_html = ''
    else:
        market_input_value_html = 'value="' + unicode_to_html(query_words) + '"'

    category_uri = ''
    category_data = []
    if category_tag:
        category_uri = category_tag.replace(':path:', '/browse/').replace(':', '/')
        category_uri = category_uri.rstrip('/')
        category_data = get_category_path_data(category_tag, language)

    canonical_url = get_search_url(category_tag=category_tag)
    localized_url = get_search_url(category_tag=category_tag, language=language)

    search_url = localized_url

    og_url = localized_url
    og_title = html_page_title
    og_description = page_description

    image_lang = 'en'
    if language == 'sv':
        image_lang = 'sv'

    og_image = 'https://static.kluemarket.com/img/kluemarket-%s.png' % image_lang

    url_params = ''
    if query_words != '':
        url_params = '&'.join([url_params, 'query=%s' % (quote_plus(unicode_to_html(query_words)))])
    if country:
        url_params = '&'.join([url_params, '&country=%s' % country])
    if latest:
        url_params = '&'.join([url_params, '&latest=true'])
    if curated is not None:
        if curated:
            url_params = '&'.join([url_params, '&curated=true'])
        else:
            url_params = '&'.join([url_params, '&curated=false'])
    if url_params != '':
        url_params = '?' + url_params

    html_results = ''
    item_html = ''
    item_is_cert = False
    show_header = True

    hreflangs = []

    item = None

    if item_uid:
        log.info("Trying to get details of item %s" % item_uid)
        item = get_item_forsale(item_uid)

    if item:
        item_url_params = url_params.lstrip('?')
        item_url_params = '%s&page=%s' % (item_url_params, page)
        item_url_params = item_url_params.lstrip('&')
        url_next_page = get_search_url(language=language, category_tag=category_tag, params=item_url_params)

        search_url = get_search_url(language=language)

        item_html = item_forsale_to_html(item, language, is_popup=False)

        # What's the item's default language?
        item_language = country_to_language(item.bdlitem.country)

        # Set page and sharing details to those of item
        canonical_url = gen_item_forsale_url(item, item_language)
        localized_url = gen_item_forsale_url(item, language)

        if item.cert_id:
            item_is_cert = True

        og_url = localized_url
        og_title = '%s | Klue Market' % item.title

        og_description = item.description
        og_description = re.sub('<[bB][rR]>', ' ', og_description)
        meta_description = og_description
        og_image = item.picture_url_w600
        html_page_title = '%s - %s %s | Klue Market' % (item.title, item.price, item.currency)
        show_header = False

        def patch_url(l):
            return '%s/%s/%s' % (get_base_url(l), translate('URL_FORSALE_LABEL', l), gen_item_forsale_title(item))
        data = get_menu_data(language, patch_url, whitefooter=True, search_url=search_url)

        # Let's find out the category path associated to this item, ie the
        # longuest :path:*: tag associated to it
        tags = [t for t in item.tags if 'path:' in t]
        tags_by_length = sorted(tags, key=lambda t: t.count(':'))
        if tags_by_length:
            category_data = get_category_path_data(':%s:' % tags_by_length[-1], language)

    else:
        def patch_url(l):
            return get_search_url(language=l, category_tag=category_tag)
        data = get_menu_data(language, patch_url, whitefooter=True, search_url=localized_url)

        # Pre-propulate first result page, for faster page loading
        results = do_search_market_html(
            query_words,
            country=country,
            page=page,
            lang=language,
            latest=latest,
            curated=curated,
            category=category_tag,
        )

        for h in results.htmls:
            html_results = html_results + "\n" + h

        url_next_page = results.url_next

    if not item:
        data['show_search_tray'] = True


    browse_data = [
        {
            'name': 'Fashion',
            'label': unicode_to_html(translate('CATEGORY_FASHION', language)),
            'url': '%s/browse/fashion' % get_base_url(language),
            'icon': 'icon-bag',
        },
        {
            'name': 'Design',
            'label': unicode_to_html(translate('CATEGORY_DESIGN', language)),
            'url': '%s/browse/design' % get_base_url(language),
            'icon': 'icon-chair',
        },
        {
            'name': 'Antics',
            'label': unicode_to_html(translate('CATEGORY_ANTICS', language)),
            'url': '%s/browse/antics' % get_base_url(language),
            'icon': 'icon-vase',
            'last': True,
        },
    ]

    return make_response(render_template(
        'market2/market.html',
        url_next_page=url_next_page,
        item_html=item_html,
        item_is_cert=item_is_cert,
        show_header=show_header,
        canonical_url=canonical_url,
        query_url=search_url,
        query_words=query_words,
        referrer=request.referrer,
        header_title_line1=header_title_line1,
        header_title_line2=header_title_line2,
        page_description=page_description,
        html_page_title=html_page_title,
        html_results=html_results,
        meta_description=meta_description,
        og_url=og_url,
        og_title=og_title,
        og_description=og_description,
        og_image=og_image,
        market_button_label=market_button_label,
        market_input_placeholder=market_input_placeholder,
        market_input_value_html=market_input_value_html,
        label_end_reached=label_end_reached,
        label_no_items_found=label_no_items_found,
        label_like_explained=unicode_to_html(translate('MARKET_LIKE_EXPLAINED', language), keep_html=True),
        label_crown_explained=unicode_to_html(translate('MARKET_CROWN_EXPLAINED', language), keep_html=True),
        label_market_explained=unicode_to_html(translate('MARKET_BUTTON_EXPLAINED', language), keep_html=True),
        url_market_explained='https://kluemarket.com/%s/%s' % (language, translate('URL_SELL_PAGE_LABEL', language)),
        focus_search=focus_search,
        category_data=category_data,
        browse_data=browse_data,
        show_browse=True if not category_tag else False,
        **data
    )), 200



#
# API to get html blocks
#

def do_search_market_html(query, page=0, country=None, lang=None, latest=False, curated=None, category=None):
    """Return a list of html items, result of a search query,
    to be inserted into main page's grid content"""

    if lang:
        language = lang
    else:
        language = get_page_language()

    if not query:
        query = ''

    if category:
        query = '%s %s' % (query, category)

    if not page:
        page = 0

    # Call the internal search api
    with backend_token() as token:

        kwargs = {
            'query': query.strip(),
            'page': page,
            'location': country,
        }

        if latest:
            kwargs['latest'] = True

        if curated is not None:
            kwargs['curated'] = curated

        items = ApiPool.api.client.search_items(**kwargs)

    if is_error(items):
        return items

    # Which url parameters are in use?
    url_params = request.query_string.decode('utf-8')

    # Convert solditems into html template for display into the search page
    htmls = []

    for item in items.items:
        normalize_item_for_sale(item, language=language)

        html = render_template(
            'market2/item.html',
            label_price=unicode_to_html(translate('MARKET_LABEL_PRICE', language)),
            label_date=unicode_to_html(translate('MARKET_LABEL_DATE', language)),
            label_in_location=unicode_to_html(translate('MARKET_LABEL_IN_LOCATION', language)),
            item_country=translate('COUNTRY_%s' % item.bdlitem.country.upper(), language),
            item=item,
            item_url=item.url,
            item_url_with_params='%s?%s' % (item.url, url_params),
            item_heart=True if item.count_views > 10 else False,
        )

        htmls.append(html)

    log.info("Found %s items ForSale" % len(htmls))

    # insert_ad(htmls)

    def patch_url(url):
        _, params = url.split('?')
        return get_search_url(language=language, params=params, category_tag=category)

    res = ApiPool.www.model.SearchResultHtml(
        query=items.query,
        count_found=items.count_found,
        url_this=patch_url(items.url_this),
        htmls=htmls,
    )

    if items.url_next:
        res.url_next = patch_url(items.url_next)

    return res


def insert_ad(htmls):
    # Insert an ad in the results
    ad = render_template(
        'marketads/ad-messenger.html',
        ad_picture='https://static.kluemarket.com/img/ad-messenger1.gif',
        ad_alt='ad background',
        ad_text='What is it worth?',
        ad_link='<a href="https://m.me/kluemarket?ref=Welcome%20message" alr="messenger">ask us on<br>Messenger!</a>',
    )
    htmls.insert(3, ad)


def do_get_item_forsale_html(id, lang=None):

    if lang:
        language = lang
    else:
        language = get_page_language()

    with backend_token() as token:
        item = ApiPool.api.client.get_item(item_id=id)

    if is_error(item):
        report_error("Failed to retrieve item %s" % id, caught=item)
        res = ApiPool.www.model.ItemHtml(
            html=''
        )
    else:
        res = ApiPool.www.model.ItemHtml(
            html=item_forsale_to_html(item, language, is_popup=True),
        )

    return res


@crash_handler
def serve_category_page(cat1=None, cat2=None, cat3=None, cat4=None):
    """Return a category page"""
    cats = [x.replace('_', ' ') for x in [cat1, cat2, cat3, cat4] if x]
    query_words = ' '.join([':%s:' % s for s in cats])
    log.info("Finding all items matching tags: %s" % query_words)
    return serve_market_page(query_words, None)


def generate_title(str_name, language):
    """Generate the page's title"""
    s = unicode_to_html(translate(str_name, language))
    return '%s | Bazardelux' % s


def gen_item_forsale_url(item, language=None):
    title = gen_item_forsale_title(item)
    if not language:
        language = country_to_language(item.bdlitem.country)
    forsale = translate('URL_FORSALE_LABEL', language)
    return '%s/%s/%s/%s' % (get_base_url(), language, forsale, title)


def gen_item_forsale_title(item):
    # Set its url attribute
    s = unidecode(html_to_unicode(item.bdlitem.title))
    s = re.sub('[^0-9a-zA-Z]+', '-', s)
    s = re.sub('[-]+', '-', s)
    s = s.strip('-')
    s = '%s_%s_%s__%s' % (s, item.bdlitem.price, item.bdlitem.currency, item.item_id)
    return s
