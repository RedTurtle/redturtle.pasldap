from persistent.mapping import PersistentMapping
from plone.protect.utils import safeWrite
from Products.PluggableAuthService.UserPropertySheet import UserPropertySheet

# import logging
from redturtle.pasldap import ldap_readonly
from redturtle.pasldap import logger


# logger = logging.getLogger(__name__)


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

        cache_key = None
        if login is not None and exact_match:
            cache_key = "login:%s" % login
        elif id is not None and exact_match:
            cache_key = "id:%s" % id
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
                if not hasattr(self, "_cache_properties"):
                    self._cache_properties = PersistentMapping()
                    safeWrite(self)
                self._cache_properties[cache_key] = sheet._properties
                safeWrite(self._cache_properties)
                return sheet
        else:
            return orig(self, user_or_group, request)

    return _wrapper
