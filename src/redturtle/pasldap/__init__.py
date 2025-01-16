"""Init and utils."""

from pas.plugins.ldap.plugin import LDAPPlugin
from pas.plugins.ldap.sheet import LDAPUserPropertySheet
from zope.i18nmessageid import MessageFactory

import logging
import os


PACKAGE_NAME = "redturtle.pasldap"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)

# increase logging
logging.getLogger("node.ext.ldap").setLevel(logging.DEBUG)

# TODO: implements readonly property in pas.plugins.ldap
ldap_readonly = False
if os.environ.get("PAS_LDAP_READWRITE", "false").lower() != "true":
    logger.info("LDAP is readonly")
    ldap_readonly = True

    def return_false(self, *args, **kwargs):
        # import pdb; pdb.set_trace()
        logger.info("LDAP %s is readonly, skipping", self)
        return False

    LDAPUserPropertySheet.canWriteProperty = return_false
    LDAPUserPropertySheet.setProperty = return_false
    LDAPUserPropertySheet.setProperties = return_false


def debug(f):
    def _wrapper(*args, **kwargs):
        logger.debug("Entering %s", f.__name__)
        import pdb

        pdb.set_trace()
        try:
            return f(*args, **kwargs)
        finally:
            logger.debug("Exiting %s", f.__name__)

    return _wrapper


def apply_patches():
    from .metrics import metricmethod
    from .resilient import resilient_enumerate_users
    from .resilient import resilient_get_properties_for_user

    # USER
    LDAPPlugin.enumerateUsers = resilient_enumerate_users(
        metricmethod(fname="enumerateUsers")(LDAPPlugin.enumerateUsers)
    )

    # TODO: caching ?
    LDAPPlugin.getPropertiesForUser = resilient_get_properties_for_user(
        metricmethod(fname="getPropertiesForUser")(LDAPPlugin.getPropertiesForUser)
    )

    # in pas.plugins.ldap getRolesForPrincipal do search with id and exact_match, that is already covered by
    # resilient_enumerate_users
    #
    # LDAPPlugin.getRolesForPrincipal = debug(metricmethod(fname="getRolesForPrincipal")(
    #     LDAPPlugin.getRolesForPrincipal
    # ))

    # TODO: disable groups in ldap
    # LDAPPlugin.enumerateGroups = metricmethod(fname="enumerateGroups")(
    #     LDAPPlugin.enumerateGroups
    # )
    # LDAPPlugin.getGroupsForPrincipal = metricmethod(fname="getGroupsForPrincipal")(
    #     LDAPPlugin.getGroupsForPrincipal
    # )
    # LDAPPlugin.getGroupById = metricmethod(fname="getGroupById")(
    #     LDAPPlugin.getGroupById
    # )


apply_patches()
