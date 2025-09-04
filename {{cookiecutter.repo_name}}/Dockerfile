# syntax=docker/dockerfile:1.7
FROM python:{{ cookiecutter.python_version }}-slim

COPY dist/ /dist/

# Install the project and its dependencies
RUN pip install -r /dist/requirements.txt && \
    pip install $(find /dist -type f -name "*.whl") && \
    rm -rf /dist

CMD ["{{ cookiecutter.cli_command }}"]
