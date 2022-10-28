"""Nox sessions."""
import nox
from nox.sessions import Session

nox.options.sessions = [
    "pre-commit",
    "tests",
]
PYTHON_VERSIONS = ["3.9", "3.10", "3.11"]


@nox.session(name="pre-commit", python=PYTHON_VERSIONS)
def precommit(session: Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or [
        "run",
        "--all-files",
        "--hook-stage=manual",
    ]
    session.install(
        "isort",
        "black",
        "autoflake",
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-builtins",
        "flake8-comprehensions",
        "flake8-docstrings",
        "flake8-eradicate",
        "pep8-naming",
        "pre-commit",
        "pre-commit-hooks",
    )
    session.run("pre-commit", *args)


@nox.session(python=PYTHON_VERSIONS)
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]

    # install the package itself into a new virtual environment with dev and tests
    # optional dependencies
    session.install(".[dev,tests]")

    # run pytest against the installed package
    session.run("pytest", *args)
