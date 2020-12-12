# mypy: allow_any_expr
(
    """
Tries to find the virtual environment used by the module being linted, and add
it to sys.path so pylint can find the imported modules.

Intended to be included in the pylint --init-hook

Easier if a section is added to pyproject.toml:
[tool.pylint.MASTER]
init-hook = ```
<this script>
```

Replace the backticks in the above snippet with triple single-quotes to allow
the escaped newlines in this file to be passed to Python, instead of being
interpreted and expanded by TOML parsing:
Multi-line literal strings
https://toml.io/en/v1.0.0-rc.1#string

Peculiarities of pylint:
Since this is being executed in an exec() Python function call, as opposed to a
normal Ptyhon script execution environment, there are some weird behaviours
that have to be worked around:
- Probably shouldn't call sys.exit()
- Names imported into the global namespace don't appear to be available in the
  scope of a defined function
- This whole module-level docstring has to be wrapped in parenthesis, otherwise
  an IndentationError is thrown
"""
)


def munge_syspath() -> None:
    "wrapping function to allow return statements to be used to halt execution"
    # pylint: disable=import-outside-toplevel
    import sys
    from pathlib import Path
    from subprocess import run
    from warnings import warn

    majorminor = f"{sys.version_info.major}.{sys.version_info.minor}"

    try:
        poetry_about = run(
            ["poetry", "about"], capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        warn("poetry not found")
        return

    if poetry_about.returncode != 0:
        warn(f"Issue with poetry\n{poetry_about.stdout}\n{poetry_about.stderr}")
        return

    poetry_env_info = run(
        "poetry env info -p", capture_output=True, text=True, shell=True, check=False
    )

    if poetry_env_info.returncode != 0:
        warn(
            f"Are we in a poetry project?\n{poetry_env_info.stdout}\n{poetry_env_info.stderr}"
        )
        return

    poetry_venv = Path(poetry_env_info.stdout.strip())

    if sys.platform == "linux":
        site_packages = poetry_venv / "lib" / f"python{majorminor}" / "site-packages"
    elif sys.platform == "win32":
        site_packages = poetry_venv / "Lib" / "site-packages"
    else:
        raise NotImplementedError(
            f"Haven't implemented pylint sys.path munging\n"
            f"to find poetry virtual environment directories on {sys.platform}"
        )

    if not site_packages.exists():
        warn("Can't find poetry virtual environment")
        return

    if str(site_packages) not in sys.path:
        sys.path.append(str(site_packages.absolute()))


munge_syspath()
