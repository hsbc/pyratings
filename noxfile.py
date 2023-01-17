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
        "autoflake >= 2.0.0",
        "black[jupyter] >= 22.12.0",
        "flake8 >= 6.0.0",
        "flake8-annotations >= 2.9.1",
        "flake8-bandit >= 4.1.1",
        "flake8-black >= 0.3.6",
        "flake8-bugbear >= 22.12.6",
        "flake8-builtins >= 2.1.0",
        "flake8-comprehensions >= 3.10.1",
        "flake8-docstrings >= 1.6.0",
        # "flake8-eradicate >= 1.3.0",
        "isort >= 5.11.4",
        "nox >= 2022.11.21",
        "pep8-naming >= 0.13.2",
        "pre-commit >= 2.20.0",
        "python-kacl >= 0.2.30",
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
