import logging
from pymacaron.exceptions import PyMacaronException
from www.io.slack import slack_error


log = logging.getLogger(__name__)


def bdl_error_reporter(title, msg):
    slack_error(title, msg)


#
# A generic error decorator setting user_message on all errors
#

error_definitions = [
    #
    # Those errors have messages set in code
    #

    ('NOT_IMPLEMENTED', 500, 'NotImplementedError', lambda s: s),
    ('INVALID_PARAMETER', 400, 'InvalidDataError', lambda s: "BUG: %s" % s),
    ('INTERNAL_SERVER_ERROR', 500, 'InternalServerError', lambda s: "WTF? %s" % s),

    #
    # Those errors have messages shown to user - subject to localization
    #


    ('NO_SUCH_ANNOUNCE', 401, 'NoSuchAnnounceError', lambda s: "Cannot find announce with id %s" % s),
    ('ES_ITEM_NOT_FOUND', 404, 'ESItemNotFoundError', lambda s: s),
]


#
# A bit of dark vodoo to dynamically generate Exception classes with individual message formatters
#

log.info("Generating %s dynamic exceptions" % (len(error_definitions)))
for code, status, classname, formatter in error_definitions:
    myexception = type(classname, (PyMacaronException, ), {"code": code, "status": status})

    def gen_init(f):

        def exception_init(self, *args, **kwargs):
            # log.info("Formatting error msg for %s with args [%s]" % (type(args), " ".join(list(args))))
            msg = f(*args, **kwargs)
            PyMacaronException.__init__(self, msg)
        return exception_init

    myexception.__init__ = gen_init(formatter)
    globals()[classname] = myexception
