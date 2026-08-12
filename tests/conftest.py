from pytest_plone import fixtures_factory
from redturtle.pasldap.testing import ACCEPTANCE_TESTING
from redturtle.pasldap.testing import FUNCTIONAL_TESTING
from redturtle.pasldap.testing import INTEGRATION_TESTING

import pytest

pytest_plugins = ["pytest_plone"]


def pytest_sessionfinish(session, exitstatus):
    # There is no test suite yet: don't fail CI because of that.
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK


globals().update(
    fixtures_factory(
        (
            (ACCEPTANCE_TESTING, "acceptance"),
            (FUNCTIONAL_TESTING, "functional"),
            (INTEGRATION_TESTING, "integration"),
        )
    )
)
