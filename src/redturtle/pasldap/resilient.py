from persistent.mapping import PersistentMapping
from plone import api
from plone.protect.utils import safeWrite
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet
from redturtle.pasldap import ldap_readonly
from redturtle.pasldap import logger


# potential users in the Zope acl_users
RESERVED_IDS = [
    "root",
    "admin",
    "adminrt",
    "rtadmin",
    "operatori_pratiche",
    "Administrators",
    "Anonymous User",
    "Site Administrators",
    "AuthenticatedUsers",
]
RESERVED_LOGINS = RESERVED_IDS

# [node.ext.ldap:511][MainThread] LDAP search with filter: (&(objectClass=person)(sAMAccountName=root))

# [redturtle.pasldap:58][MainThread] func=pas.plugins.ldap.plugin.enumerateUsers info=None args=(<LDAPPlugin at /.../acl_users/pasldap>,) kwargs={'id': None, 'login': None, 'exact_match': False, 'sort_by': None, 'max_results': None, 'fullname': 'mario'} elapsed=32ms threshold=-1ms 🤔

# [redturtle.pasldap:58][MainThread] func=pas.plugins.ldap.plugin.enumerateUsers info=None args=(<LDAPPlugin at /.../acl_users/pasldap>,) kwargs={'id': None, 'login': None, 'exact_match': False, 'sort_by': None, 'max_results': None, 'email': 'mario'} elapsed=38ms threshold=-1ms 🤔

# XXX: se si fa una ricerca sul pannello di controllo, ad esempio con "mario" vengono comunque interrogati (almeno una volta)
#      tutti gli utenti dell'ldap ( !?)


# OPIONINATED
def resilient_enumerate_users(orig):
    def _wrapper(
        self,
        id=None,
        login=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw,
    ):
        # XXX: manually manage query like kw:{'id': 'user@example.com*'} exact_match:False
        if kw.keys() == ["id"] and not exact_match:
            logger.debug("convert wrong query kw:%s exact_match:%s", kw, exact_match)
            exact_match = True
            kw["id"] = kw["id"].strip("*")

        # kwargs={'id': 'xxx', 'login': None, 'exact_match': False, 'sort_by': None, 'max_results': None}
        if kw.get("id") and "*" not in kw["id"] and not exact_match:
            logger.debug("convert wrong query kw:%s exact_match:%s", kw, exact_match)
            exact_match = True

        cache_key = None
        if login is not None and exact_match:
            cache_key = "login:%s" % login
            if login in RESERVED_LOGINS:
                return []
        elif id is not None and exact_match:
            cache_key = "id:%s" % id
            if id in RESERVED_IDS:
                return []
        if (
            cache_key
            and hasattr(self, "_cache_users")
            and cache_key in self._cache_users
        ):
            # logger.info("HIT: %s", cache_key)
            return self._cache_users[cache_key]

        # TODO: analyze when invalidate, but at then exact_match search for users
        #       could be safe until user is deleted and beyond....

        users = orig(
            self,
            id=id,
            login=login,
            exact_match=exact_match,
            sort_by=sort_by,
            max_results=max_results,
            **kw,
        )

        if cache_key:
            logger.info("MISS: enumerateUsers %s", cache_key)
            if not users:
                local_users = api.portal.get_tool("acl_users").source_users
                local_groups = api.portal.get_tool("acl_users").source_groups
                if not local_users.enumerateUsers(
                    id=id, login=login, exact_match=True
                ) and not local_groups.enumerateGroups(
                    id=id, login=login, exact_match=True
                ):
                    # TODO: verificare se il risultato vuoto è un errore (da non mettere in cache) o veramente
                    #       un risultato vuoto (da mettere in cache? solo temporaneamente?)
                    logger.warning(
                        "enumerateUsers %s not found (possible error? not caching?)",
                        cache_key,
                    )
                    return users
            if not hasattr(self, "_cache_users"):
                self._cache_users = PersistentMapping()
                safeWrite(self)
            self._cache_users[cache_key] = users
            safeWrite(self._cache_users)

        return users

    return _wrapper


# OPINIONATED
def resilient_get_properties_for_user(orig):
    def _wrapper(self, user_or_group, request=None):
        if ldap_readonly:
            # TODO: analyze when invalidate, maybe after the user logged in
            cache_key = user_or_group.getId()
            # TODO: user_or_group.isGroup() and group plugin not active ....
            if user_or_group.getId() in RESERVED_IDS:
                return {}

            if hasattr(self, "_cache_properties") and isinstance(
                self._cache_properties.get(cache_key), dict
            ):
                # logger.info("HIT: %s", cache_key)
                return UserPropertySheet(
                    self.getId(),
                    schema=None,
                    **self._cache_properties[cache_key],
                )
            else:
                logger.info("MISS: getPropertiesForUser %s", cache_key)
                sheet = orig(self, user_or_group, request)
                if sheet == {}:
                    # XXX: no result, caching no result
                    properties = {}
                elif not hasattr(sheet, "_properties"):
                    logger.warning("missing _properies for %s", cache_key)
                    return sheet
                else:
                    properties = sheet._properties
                if not hasattr(self, "_cache_properties"):
                    self._cache_properties = PersistentMapping()
                    safeWrite(self)
                self._cache_properties[cache_key] = properties
                safeWrite(self._cache_properties)
                return sheet
        else:
            return orig(self, user_or_group, request)

    return _wrapper
