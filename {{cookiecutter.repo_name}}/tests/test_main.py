from {{ cookiecutter.package_name }}.main import main


def test_main():
    """Test that main runs without errors."""
    main()
