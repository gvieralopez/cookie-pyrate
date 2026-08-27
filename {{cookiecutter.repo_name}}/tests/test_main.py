from {{ cookiecutter.package_name }}.main import main


def test_main() -> None:
    """Test that main runs without errors."""
    main()
