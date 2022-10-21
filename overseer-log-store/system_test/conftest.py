def pytest_addoption(parser):
    parser.addoption(
        "-E",
        "--base_endpoint",
        help="the service endpoint root of the to-be-tested overseer",
    )
    parser.addoption(
        "-P",
        "--protocol",
        help="the connection protocol, default [https]",
        default="https",
    )
    parser.addoption(
        "-T",
        "--timeout",
        default=3,
    )
