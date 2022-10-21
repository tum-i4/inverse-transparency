""" System tests verifying basic health of a running Overseer server. """

import pytest
import requests


@pytest.fixture
def endpoint(request):
    base_endpoint = request.config.getoption("--base_endpoint")
    protocol = request.config.getoption("--protocol")
    return protocol + "://" + base_endpoint


@pytest.fixture
def timeout(request):
    return int(request.config.getoption("--timeout"))


def test_system_health(endpoint, timeout):
    """test external overseer running and database connected"""
    r = requests.get(f"{endpoint}/health", timeout=timeout)
    assert r.status_code == 200
