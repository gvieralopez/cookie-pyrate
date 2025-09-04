import os
import logging
import {{ cookiecutter.package_name }}

logger = logging.getLogger(__name__)

COOKIE_PYRATE_VERSION = os.getenv("COOKIE_PYRATE_VERSION", "Not Set")

def main() -> None:
    pkg = "{{ cookiecutter.package_name }}"
    version = {{ cookiecutter.package_name }}.__version__
    
    logger.info("Package '%s' installed with version: %s", pkg, version)
    logger.info("Generated using Cookie Pyrate Version: %s", COOKIE_PYRATE_VERSION)
    
    logger.info("Life is beautiful!")

if __name__ == "__main__":
    main()
