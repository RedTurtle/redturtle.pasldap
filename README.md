# redturtle.pasldap

A new addon for Plone

## Features

* [ ] Check the pas.plugins.ldap configuration for best practices, such as read/connection timeouts, memcached usage, handling many users, etc.
* [ ] Log LDAP queries to investigate long processing times and unnecessary operations (ensure passwords are not logged for security).
* [ ] Make LDAP operations resilient by persistently caching certain queries (opinionated suggestion).
* [ ] Intercept errors such as "Problems getting group_ids!" caused by misconfigurations.
* [ ] During testing I saw some call to enumerateUsers with `criteria:{'id': 'user@example.com*'} exact_match:False`, ... 
* [ ] ...


We need a profile installation here? (maybe not)

We need restapi here? (maybe not)


## pas.plugins.ldap hidden gems

```
LDAP_ERROR_LOG_TIMEOUT = float(
    os.environ.get("PAS_PLUGINS_LDAP_ERROR_LOG_TIMEOUT", 300.0)
)
LDAP_LONG_RUNNING_LOG_THRESHOLD = float(
    os.environ.get("PAS_PLUGINS_LDAP_LONG_RUNNING_LOG_THRESHOLD", 5.0)
)
```

## Installation

Install redturtle.pasldap with `pip`:

```shell
pip install redturtle.pasldap
```

And to create the Plone site:

```shell
make create_site
```

## Development

Local ldap server:

```
cd tests/docker-test-openldap
docker compose build
docker compose up
```

Verify that ldap is working:

```
LDAPTLS_REQCERT=never ldapsearch -H ldap://localhost:10389 -ZZ -x -b "ou=people,dc=planetexpress,dc=com" -D "cn=admin,dc=planetexpress,dc=com" -w GoodNewsEveryone "(objectClass=inetOrgPerson)"
```

```
make buil-dev

PLONE_REGISTRY_YAML=tests/docker-test-openldap/regenv.yaml LDAPTLS_REQCERT=never make start
```

## Contribute


- [Issue Tracker](https://github.com/RedTurtle/redturtle.pasldap/issues)
- [Source Code](https://github.com/RedTurtle/redturtle.pasldap/)

## License

The project is licensed under GPLv2.

## Credits and Acknowledgements 🙏

Crafted with care by **Generated using [Cookieplone (0.8.2)](https://github.com/plone/cookieplone) and [cookiecutter-plone (d9b5293)](https://github.com/plone/cookiecutter-plone/commit/d9b52933cbc6efd137e93e35a270214e307359f0) on 2025-01-15 23:35:38.896932**. A special thanks to all contributors and supporters!
