# 🏴‍☠️ Cookie Pyrate

A Python [cookiecutter](https://cookiecutter.readthedocs.io) template that keeps things **simple, modern, and ready to sail**.  
Powered by [uv](https://docs.astral.sh/uv/) for fast dependency management and designed to give you a clean project structure from the start.


## ⚡ Usage

Make sure you have [uv](https://docs.astral.sh/uv/) installed.  
Then, with **just one command**, you can set sail and create your new project:

```bash
uvx cookiecutter gh:gvieralopez/cookie-pyrate
```

Follow the prompts to name your treasure (project 🏴‍☠️), and you’ll have a fresh repo scaffolded in seconds.
Next, `cd` into your new project folder and check the generated `README.md` for details.


## 📦 What’s Inside

### ⚙️ Main Project Files

* **pyproject.toml** → preconfigured metadata, dependencies, and tool settings
* **uv.lock** → generated per project and committed for reproducible environments
* **.gitignore** → tailored for modern Python projects
* **README.md** → scaffolded with your project details, ready to publish
* **.env templates** → simplify configuration for development and testing
* **.python-version** → tells *uv* which Python version to use

### 🧑‍💻 Tooling

* **uv** → ultra-fast dependency and environment management
* **Ruff** → combined linting and formatting in one tool
* **MyPy** → static type checking for safer code
* **Pytest** → testing framework with built-in coverage support
* **ebump** → automatic project versioning
* **Makefile** → one entrypoint for common tasks, no more memorizing CLI flags

### 🚀 Extra Tools (Optional)

* **mkDocs** → quick web-based documentation generated from markdown  
* **LICENSE**  → auto-generate license file based on chosen license
* **pre-commits**  → pre-commit hooks for quality assurance checks
* **Production Dockerfile** → ready-to-use container for production deployment
* **GitHub Actions pipeline (optional)** → a pinned QA action caller

### GitHub Actions Pipelines

CI/CD is opt-in during project generation. Choose GitHub Actions to include the
pinned QA workflow, or choose None. The workflow calls the shared `run-qa`
action in this repository's `github-actions` directory.

## 🗺️ Roadmap

* [ ] `windows compatibility` → improve Windows support  
* [ ] `pipelines` → support for Bitbucket, GitLab, and GitHub pipelines  
* [ ] `agents` → support for agents and skills config


## 🤝 Contributing

PRs, issues, and new ideas are welcome!


## 💙 Say Thanks

If this template saved you time (or gave you a good laugh 🏴‍☠️🍪🐍),  
please consider giving the repo a ⭐ on GitHub — it really helps paying my bills!

---

_Disclaimer: This template reflects my opinionated vision of what a modern 
Python project should look like._
