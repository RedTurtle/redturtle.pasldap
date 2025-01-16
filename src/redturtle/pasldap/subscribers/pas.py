from plone import api
from plone.protect.utils import safeWrite
from redturtle.pasldap import logger


def loggedin(event):
    print("Logged in")
    cache_key = event.principal.getId()
    portal = api.portal.get()
    for psheet in event.principal.getOrderedPropertySheets():
        try:
            plugin = portal.acl_users[psheet._id]
            if (
                hasattr(plugin, "_cache_properties")
                and plugin._cache_properties[cache_key]
            ):
                logger.info("Clearing cache for %s", cache_key)
                del plugin._cache_properties[cache_key]
                safeWrite(plugin._cache_properties)
        except:  # NOQA
            pass
