# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible

import logging
import gettext
from collections import namedtuple
import importlib
import sys

BackendRegistryEntry = namedtuple('BackendRegistryEntry', ('verbose_name', 'store_class'))

REGISTERED_BACKENDS = {
    'sqlalchemy': BackendRegistryEntry('SQLAlchemy', 'hamsterlib.backends.sqlalchemy.SQLAlchemyStore'),
}

# See: https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef#gettext
kwargs = {}
if sys.version_info < (3,):
    kwargs['unicode'] = True
gettext.install('hamsterlib', **kwargs)


@python_2_unicode_compatible
class HamsterControl(object):
    """
    All mandatory config options are set as part of the contoler setup.
    Any client may overwrite those values. but we can always asume that the
    controler does have a value set.

    We will try hard to get through with at least always returning the object.
    We should be able to change only the internal service code to then
    decompose it into its required weired format.

    We were compelled to make attach CRUD-methods to our activity, category
    and fact objects. But as all of those depend on access to the store
    anyway they seem to be best be placed here as a central hub.

    Generic CRUD-actions is to be delegated to our store. The Controler itself
    provides general timetracking functions so that our clients do not have to.
    """

    def __init__(self, config):
        self.config = config
        self.lib_logger = self._get_logger()
        self.store = self._get_store()
        # convinience attributes
        self.categories = self.store.categories
        self.activities = self.store.activities
        self.facts = self.store.facts

    def _get_store(self):
        """
        Setup the store used by this controler.

        This method is in charge off figuring out the store type, its instantiation
        as well as all additional configuration.
        """

        backend = REGISTERED_BACKENDS.get(self.config['store'])
        if not backend:
            raise KeyError(_("No or invalid storage specified."))
        import_path, storeclass = tuple(backend.store_class.rsplit('.', 1))

        backend_module = importlib.import_module(import_path)
        cls = getattr(backend_module, storeclass)
        return cls(self.config)

    def _get_logger(self):
        """
        Setup and configure the main logger.

        As the docs suggest we setup just a pseudo handler. Any client that actually
        wants to use logging needs to setup its required handlers itself.
        """

        lib_logger = logging.getLogger('hamsterlib.lib')
        lib_logger.addHandler(logging.NullHandler())
        return lib_logger
