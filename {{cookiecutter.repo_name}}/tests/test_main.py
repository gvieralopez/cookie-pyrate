import os
import logging
import pytest
import {{ cookiecutter.package_name }}

from {{ cookiecutter.package_name }} import main

def test_main_logs(caplog):
    # Capture logs
    with caplog.at_level(logging.INFO):
        main()

    # Check that package name and version are logged
    pkg_name = "{{ cookiecutter.package_name }}"
    pkg_version = {{ cookiecutter.package_name }}.__version__
    assert f"Package '{pkg_name}' installed with version: {pkg_version}" in caplog.text

    # Check that COOKIE_PYRATE_VERSION is logged (the env var we set in .env.test)
    assert "Generated using Cookie Pyrate Version: 1.2.3" in caplog.text

    # Check that the final message is logged
    assert "Life is beautiful!" in caplog.text
