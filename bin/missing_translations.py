#!/usr/bin/env python3
import os
import sys
import json
import logging
import click

PATH_LIBS_HERE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
PATH_LIBS_API = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'bdl-api')
sys.path.append(PATH_LIBS_HERE)
sys.path.append(PATH_LIBS_API)

from bdl.tagger import get_tree
from www.localisation import TRANSLATIONS


log = logging.getLogger(__name__)


log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(message)s')
# handler.setFormatter(formatter)
log.addHandler(handler)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)


@click.command()
def main():
    """Look at all categories under ../bdl-api/etc and add to translations.json
    those that are missing.

    """

    tree = get_tree()

    for n in tree.get_all_nodes():
        name = n.name
        translation = n.translation
        cat = 'CATEGORY_%s' % name.upper()

        if cat not in TRANSLATIONS:
            print('  "%s": {"en": "%s"},' % (cat, translation))


if __name__ == "__main__":
    main()
