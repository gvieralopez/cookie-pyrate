# syntax=docker/dockerfile:1.7
FROM python:{{ cookiecutter.python_version }}-slim

COPY dist/ /dist/

# Install the project and its dependencies
RUN pip install -r /dist/requirements.txt && \
    pip install $(find /dist -type f -name "*.whl") && \
    rm -rf /dist
{% if cookiecutter.cli_command %}
CMD ["{{ cookiecutter.cli_command }}"]
{% else %}
CMD ["python", "-m", "{{ cookiecutter.package_name }}"]
{% endif %}
