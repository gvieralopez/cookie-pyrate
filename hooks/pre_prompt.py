import functools
import json
import subprocess
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path

from cookiecutter.generate import generate_context
from cookiecutter.prompt import prompt_for_config, render_variable


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            cls.instance = cls._instances[cls]
        return cls._instances[cls]


class PromptProcess(metaclass=SingletonMeta):
    def __init__(self, context):
        self.env = None
        self.context = context
        self.conditions = context["cookiecutter"].pop("__conditions__", {})
        self.cookiecutter = {}
        self.ignored_keys = []

    @staticmethod
    def wraps(func_path):
        def decorator(wrapper):
            try:
                module_path, func_name = func_path.rsplit(".", 1)
            except ValueError:
                raise ImportError(f"{func_path} doesn't look like a module path")

            try:
                module = sys.modules[module_path]
            except KeyError:
                try:
                    module = import_module(module_path)
                except ImportError as e:
                    raise ImportError(f"Could not import module {module_path}: {e}")

            try:
                function = getattr(module, func_name)
            except AttributeError:
                raise AttributeError(
                    f"Function {func_name} not found in module {module_path}"
                )

            @functools.wraps(function)
            def wrapped(*args, **kwargs):
                return wrapper(PromptProcess.instance, function, *args, **kwargs)

            # Replace the original function with the wrapped version
            setattr(module, func_name, wrapped)

            return wrapper

        return decorator

    @wraps("cookiecutter.prompt.render_variable")
    def render_variable(self, func, env, raw, cookiecutter_dict):
        """Initialize the `env` & `cookiecutter` attrs."""
        self.env = env
        self.cookiecutter = cookiecutter_dict
        return func(env, raw, cookiecutter_dict)

    @wraps("cookiecutter.prompt.read_user_choice")
    def read_user_choice(self, func, *args, **kwargs):
        return self.apply_read_user_func(func, *args, **kwargs)

    @wraps("cookiecutter.prompt.read_user_yes_no")
    def read_user_yes_no(self, func, *args, **kwargs):
        return self.apply_read_user_func(func, *args, **kwargs)

    @wraps("cookiecutter.prompt.read_user_variable")
    def read_user_variable(self, func, *args, **kwargs):
        return self.apply_read_user_func(func, *args, **kwargs)

    def prompt_user(self):
        user_prompts = {
            k: v
            for k, v in prompt_for_config(self.context).items()
            if k not in self.ignored_keys
        }
        for key in self.ignored_keys:
            user_prompts[key] = self.context["cookiecutter"][key]
        return user_prompts

    def apply_read_user_func(self, func, key, *args, **kwargs):
        if key in self.conditions:
            condition = self.conditions[key]
            try:
                is_met = eval(render_variable(self.env, condition, self.cookiecutter))
            except SyntaxError:
                is_met = False
            if not is_met:
                self.ignored_keys.append(key)
                return None
        return func(key, *args, **kwargs)


def _run_command(command: list[str], default: str, timeout: int = 5) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except subprocess.SubprocessError:
        return default


def _get_git_config(key: str, default: str) -> str:
    return _run_command(["git", "config", "--global", key], default=default)


def get_author_name_from_git(default: str) -> str:
    return _get_git_config("user.name", default)


def get_author_email_from_git(default: str) -> str:
    return _get_git_config("user.email", default)


def get_current_year() -> str:
    return str(datetime.now().year)


def update_cookiecutter_json(updates: dict[str, str]) -> None:
    config_path = Path("cookiecutter.json")
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data.update(updates)
    config_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    updates = {
        "author_name": get_author_name_from_git(default="Gustavo Viera López"),
        "author_email": get_author_email_from_git(default="gvieralopez@gmail.com"),
        "year": get_current_year(),
    }

    context = generate_context()
    context["cookiecutter"].update(updates)
    prompt_process = PromptProcess(context)

    cookiecutter = prompt_process.prompt_user()
    update_cookiecutter_json(cookiecutter)
