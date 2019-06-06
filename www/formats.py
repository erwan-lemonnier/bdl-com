import re
import pprint
import logging
from bravado_core.formatter import SwaggerFormat
from bravado_core.exception import SwaggerValidationError


log = logging.getLogger(__name__)


formats = []

def _create_format(name, validate):
    formats.append(
        SwaggerFormat(
            format=name,
            to_wire=lambda s: s,
            to_python=lambda s: s,
            validate=validate,
            description="custom format {0}".format(name)
        )
    )


def get_custom_formats():
    return formats

#
# Custom formats
#

def validate_is_ascii(s):
    if s is None:
        raise SwaggerValidationError("String is None: " + pprint.pformat(s))
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        raise SwaggerValidationError("Parameter contains non-ascii unicode characters: " + pprint.pformat(s))


# All currencies supported by stripe
supported_currencies = (
    "AED", "ALL", "ANG", "ARS", "AUD", "AWG", "BBD", "BDT", "BIF", "BMD", "BND", "BOB",
    "BRL", "BSD", "BWP", "BZD", "CAD", "CHF", "CLP", "CNY", "COP", "CRC", "CVE", "CZK",
    "DJF", "DKK", "DOP", "DZD", "EGP", "ETB", "EUR", "FJD", "FKP", "GBP", "GIP", "GMD",
    "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "ISK",
    "JMD", "JPY", "KES", "KHR", "KMF", "KRW", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD",
    "MAD", "MDL", "MNT", "MOP", "MRO", "MUR", "MVR", "MWK", "MXN", "MYR", "NAD", "NGN",
    "NIO", "NOK", "NPR", "NZD", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR",
    "RUB", "SAR", "SBD", "SCR", "SEK", "SGD", "SHP", "SLL", "SOS", "STD", "SVC", "SZL",
    "THB", "TOP", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VND", "VUV",
    "WST", "XAF", "XOF", "XPF", "YER", "ZAR", "AFN", "AMD", "AOA", "AZN", "BAM", "BGN",
    "CDF", "GEL", "KGS", "LSL", "MGA", "MKD", "MZN", "RON", "RSD", "RWF", "SRD", "TJS",
    "TRY", "XCD", "ZMW")


def validate_amount(string):
    if type(string) is int or type(string) is float:
        return
    validate_is_ascii(string)
    if not re.match(r"^[0-9]+(\.[0-9]+)?$", str(string)):
        raise SwaggerValidationError("Invalid Amount {0}".format(string))
_create_format('amount', validate_amount)


def validate_currency(string):
    validate_is_ascii(string)
    if string not in supported_currencies:
        raise SwaggerValidationError("Invalid currency {0}".format(string))
_create_format('currency', validate_currency)


def validate_email(string):
    validate_is_ascii(string)
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", string):
        raise SwaggerValidationError("Invalid email {0}".format(string))
_create_format('email', validate_email)


def validate_password_hash(string):
    validate_is_ascii(string)
    if not re.match(r'^[0-9a-f]{16}$', string):
        raise SwaggerValidationError("Invalid password hash {0}".format(string))
_create_format('password_hash', validate_password_hash)


def validate_four_digits(string):
    validate_is_ascii(string)
    if not re.match(r'^[0-9]{4}$', string):
        raise SwaggerValidationError("Invalid card 4 digits {0}".format(string))
_create_format('four_digits', validate_four_digits)



# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
iso6391_languages = [
    'ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae',
    'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn', 'bh', 'bi', 'bs', 'br', 'bg',
    'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cv', 'kw', 'co', 'cr', 'hr', 'cs',
    'da', 'dv', 'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr',
    'ff', 'gl', 'ka', 'de', 'el', 'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi',
    'ho', 'hu', 'ia', 'id', 'ie', 'ga', 'ig', 'ik', 'io', 'is', 'it', 'iu',
    'ja', 'jv', 'kl', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv',
    'kg', 'ko', 'ku', 'kj', 'la', 'lb', 'lg', 'li', 'ln', 'lo', 'lt', 'lu',
    'lv', 'gv', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mh', 'mn', 'na',
    'nv', 'nb', 'nd', 'ne', 'ng', 'nn', 'no', 'ii', 'nr', 'oc', 'oj', 'cu',
    'om', 'or', 'os', 'pa', 'pi', 'fa', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn',
    'ro', 'ru', 'sa', 'sc', 'sd', 'se', 'sm', 'sg', 'sr', 'gd', 'sn', 'si',
    'sk', 'sl', 'so', 'st', 'az', 'es', 'su', 'sw', 'ss', 'sv', 'ta', 'te',
    'tg', 'th', 'ti', 'bo', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw',
    'ty', 'ug', 'uk', 'ur', 'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'fy',
    'xh', 'yi', 'yo', 'za', 'zu',
]

def validate_language(string):
    validate_is_ascii(string)
    if string not in iso6391_languages:
        raise SwaggerValidationError("Invalid iso639-1 language {0}".format(string))
_create_format('language', validate_language)


iso3166_1_locales = [
    'AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
    'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BV', 'BR',
    'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC',
    'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO',
    'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 'GA',
    'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT',
    'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP',
    'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI',
    'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX',
    'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI',
    'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN',
    'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS',
    'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS',
    'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK',
    'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY', 'UZ', 'VU',
    'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW'
]

iso3166_1_alpha2 = [
    'AF', 'AX', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ',
    'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BQ', 'BA', 'BW', 'BV', 'BR',
    'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC',
    'CO', 'KM', 'CG', 'CD', 'CK', 'CR', 'CI', 'HR', 'CU', 'CW', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO',
    'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'TF', 'GA',
    'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT',
    'HM', 'VA', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP',
    'JE', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI',
    'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX',
    'FM', 'MD', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI',
    'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN',
    'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'BL', 'SH', 'KN', 'LC', 'MF', 'PM', 'VC', 'WS',
    'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SX', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'SS',
    'ES', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK',
    'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'GB', 'US', 'UM', 'UY', 'UZ', 'VU',
    'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW'
]

iso3166_1_alpha3 = [
    'ABW', 'AFG', 'AGO', 'AIA', 'ALA', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATA', 'ATF', 'ATG',
    'AUS', 'AUT', 'AZE', 'BDI', 'BEL', 'BEN', 'BES', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLM',
    'BLR', 'BLZ', 'BMU', 'BOL', 'BRA', 'BRB', 'BRN', 'BTN', 'BVT', 'BWA', 'CAF', 'CAN', 'CCK', 'CHE',
    'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CXR',
    'CYM', 'CYP', 'CZE', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESH', 'ESP',
    'EST', 'ETH', 'FIN', 'FJI', 'FLK', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GGY', 'GHA', 'GIB',
    'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GRL', 'GTM', 'GUF', 'GUM', 'GUY', 'HKG', 'HMD',
    'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IMN', 'IND', 'IOT', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA',
    'JAM', 'JEY', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN',
    'LBR', 'LBY', 'LCA', 'LIE', 'LKA', 'LSO', 'LTU', 'LUX', 'LVA', 'MAC', 'MAF', 'MAR', 'MCO', 'MDA',
    'MDG', 'MDV', 'MEX', 'MHL', 'MKD', 'MLI', 'MLT', 'MMR', 'MNE', 'MNG', 'MNP', 'MOZ', 'MRT', 'MSR',
    'MTQ', 'MUS', 'MWI', 'MYS', 'MYT', 'NAM', 'NCL', 'NER', 'NFK', 'NGA', 'NIC', 'NIU', 'NLD', 'NOR',
    'NPL', 'NRU', 'NZL', 'OMN', 'PAK', 'PAN', 'PCN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRK',
    'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'SAU', 'SDN', 'SEN', 'SGP', 'SGS',
    'SHN', 'SJM', 'SLB', 'SLE', 'SLV', 'SMR', 'SOM', 'SPM', 'SRB', 'SSD', 'STP', 'SUR', 'SVK', 'SVN',
    'SWE', 'SWZ', 'SXM', 'SYC', 'SYR', 'TCA', 'TCD', 'TGO', 'THA', 'TJK', 'TKL', 'TKM', 'TLS', 'TON',
    'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UGA', 'UKR', 'UMI', 'URY', 'USA', 'UZB', 'VAT', 'VCT',
    'VEN', 'VGB', 'VIR', 'VNM', 'VUT', 'WLF', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE'
]

def validate_country_code(string):
    validate_is_ascii(string)
    if string.strip() not in iso3166_1_alpha2:
        raise SwaggerValidationError("Invalid or unsupported iso-3166-1 alpha2 country code {0}".format(string))
_create_format('country_code', validate_country_code)

def validate_country_code_alpha3(string):
    validate_is_ascii(string)
    if string.strip() not in iso3166_1_alpha3:
        raise SwaggerValidationError("Invalid or unsupported iso-3166-1 alpha3 country code {0}".format(string))
_create_format('country_code_alpha3', validate_country_code_alpha3)


def validate_s3_url(string):
    validate_is_ascii(string)
    if 'http' not in string:
        raise SwaggerValidationError("Invalid s3_url {0}".format(string))
_create_format('s3_url', validate_s3_url)


def validate_picture_url(string):
    validate_is_ascii(string)
    if 'http' not in string:
        raise SwaggerValidationError("Invalid picture url {0}. Should contain 'http'.".format(string))
    # Make sure the url contains png|jpg|jpeg
    s = string.lower()
    if 'jpg' not in s and 'jpeg' not in s and 'png' not in s:
        raise SwaggerValidationError("Invalid picture url {0}. Should contain 'jpg', 'jpeg' or 'png'.".format(string))
_create_format('picture_url', validate_picture_url)


def validate_s3_key(string):
    validate_is_ascii(string)
    if '/' not in string:
        raise SwaggerValidationError("Invalid S3 Key {0} (should contain '/')".format(string))
    elems = string.split('/')
    if not len(elems) == 2:
        raise SwaggerValidationError("Invalid S3 Key {0} (key should have 2 elements separated by '/')".format(string))
    # Allow mock objects to share the same pictures, located in the mock s3
    # bucket, to avoid cloter in incoming bucket
    if elems[0] != 'mock':
        try:
            validate_item_id(elems[0])
        except SwaggerValidationError:
            raise SwaggerValidationError("Invalid S3 Key {0} (first part of the key is not an item_id)".format(string))
    if not re.match(r"^[0-9\-\_a-z]+\.(png|jpg|jpeg)$", elems[1], re.IGNORECASE):
        raise SwaggerValidationError("Invalid S3 Key {0} (key name should be <integer-letters-dash>.jpg)".format(string))
_create_format('s3_key', validate_s3_key)


def validate_yyyy_mm_dd(string):
    validate_is_ascii(string)
    if not re.match(r"^[12][0-9]{3}-[0-9]{2}-[0-9]{2}$", string):
        raise SwaggerValidationError("Invalid YYYY-MM-DD date {0}".format(string))
    y, m, d = string.split('-')
    if int(m) == 0 or int(m) > 12:
        raise SwaggerValidationError("Invalid YYYY-MM-DD date {0}".format(string))
    if int(d) == 0 or int(d) > 31:
        raise SwaggerValidationError("Invalid YYYY-MM-DD date {0}".format(string))

_create_format('yyyy_mm_dd', validate_yyyy_mm_dd)
