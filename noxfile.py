"""Nox sessions."""
import nox
from nox.sessions import Session

nox.options.sessions = [
    "tests",
]


@nox.session(python=["3.9", "3.10"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]

    # install the package itself into a new virtual environment with dev and tests
    # optional dependencies
    session.install(".[dev,tests]")

    # run pytest against the installed package
    session.run("pytest", *args)
