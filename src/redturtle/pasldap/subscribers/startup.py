# from plone import api
# from zope.component.hooks import setSite
from pas.plugins.ldap.plugin import ILDAPPlugin
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.PlonePAS import interfaces as plonepas_interfaces
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces

import logging


logger = logging.getLogger(__name__)


def site_load(event):
    conn = event.database.open()
    try:
        app = conn.root()["Application"]
        for key, portal in app.items():
            if IPloneSiteRoot.providedBy(portal):
                logger.info("Check: %s", key)
                plugins = [
                    (key, item)
                    for (key, item) in portal.acl_users.items()
                    if ILDAPPlugin.providedBy(item)
                ]
                if not plugins:
                    # No ldap plugin installed
                    continue
                if len(plugins) > 1:
                    # More than one ldap plugin installed
                    logger.warning(
                        "[LDAP] More than one ldap plugin installed: %s",
                        ", ".join([key for (key, _) in plugins]),
                    )
                for _, plugin in plugins:
                    check_pas(plugin)
                # setSite(item)

                # check registry for
                # plone.many_users and plone.many_groups

                # XXX: verify using collective.regenv
                # if not portal.portal_registry.get("plone.many_users"):
                #     logger.warning("[LDAP] plone.many_users not set")

    finally:
        conn.close()


def check_pas(plugin):
    # import pdb; pdb.set_trace()
    # TODO: enumerateUsers deve essere dopo, rispetto a source_users e mutable_properties
    #       in modo che le risoluzioni locali avvengano subito
    logger.info("  Check plugin: %s", plugin.getId())
    if plugin.is_plugin_active(pas_interfaces.IGroupEnumerationPlugin):
        logger.warning(
            "    [WARNING] GroupEnumerationPlugin is active => evaluate to disable"
        )
    if plugin.is_plugin_active(pas_interfaces.IGroupsPlugin):
        logger.warning("    [WARNING] GroupsPlugin is active => evaluate to disable")
    if plugin.is_plugin_active(plonepas_interfaces.group.IGroupIntrospection):
        logger.warning(
            "    [WARNING] GroupIntrospection is active => evaluate to disable"
        )
    if plugin.is_plugin_active(plonepas_interfaces.group.IGroupManagement):
        logger.warning("    [WARNING] GroupManagement is active => evaluate to disable")

    # if plugin.is_plugin_active(pas_interfaces.IPropertiesPlugin):
    #     logger.warning("    [WARNING] PropertiesPlugin is active => evaluate to disable")
    # if plugin.is_plugin_active(pas_interfaces.IRoleEnumerationPlugin):
    #     logger.warning("    [WARNING] RoleEnumerationPlugin is active => evaluate to disable")
    if plugin.is_plugin_active(pas_interfaces.IUserAdderPlugin):
        logger.warning("    [WARNING] UserAdderPlugin is active => evaluate to disable")
    # if plugin.is_plugin_active(pas_interfaces.IUserEnumerationPlugin):
    #     logger.warning("    [WARNING] UserEnumerationPlugin is active => evaluate to disable")
    if plugin.is_plugin_active(plonepas_interfaces.plugins.IUserManagement):
        logger.warning("    [WARNING] UserManagement is active => evaluate to disable")
    if plugin.is_plugin_active(pas_interfaces.IUpdatePlugin):
        logger.warning("    [WARNING] UpdatePlugin is active => evaluate to disable")
