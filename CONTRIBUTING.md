<!-- omit in toc -->
# Contributing to _pyratings_

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the
[Table of Contents](#table-of-contents) for different ways to help and details about
how this project handles them. Please make sure to read the relevant section before
making your contribution. It will make it a lot easier for us maintainers and smooth
out the experience for all involved. The community looks forward to your contributions. 🎉

> And if you like the project, but just don't have time to contribute, that's fine.
There are other easy ways to support the project and show your appreciation, which we
would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's README
> - Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
    - [Reporting Bugs](#reporting-bugs)
    - [Suggesting Enhancements](#suggesting-enhancements)
    - [Your First Code Contribution](#your-first-code-contribution)
    - [Improving The Documentation](#improving-the-documentation)
- [Style guides](#style-guides)
    - [Code formatting](#code-formatting)
    - [Linting](#linting)
    - [Commit Messages](#commit-messages)
- [Attribution](#attribution)


## Code of Conduct

This project and everyone participating in it is governed by the
[pyratings Code of Conduct](https://hsbc.github.io/pyratings/code_of_conduct/).
By participating, you are expected to uphold this code. Please report unacceptable
behavior to <opensource@hsbc.com>.


## I Have a Question

> If you want to ask a question, we assume that you have read the available
[Documentation](https://hsbc.github.io/pyratings/).

Before you ask a question, it is best to search for existing
[Issues](https://github.com/hsbc/pyratings/issues?q=is%3Aissue) that might help you.
In case you have found a suitable issue and still need clarification, you can write 
your question in this issue.

If you then still feel the need to ask a question and need clarification, we recommend
the following:

- Open a new [Issue](https://github.com/hsbc/pyratings//issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Python version etc.), depending on what seems 
  relevant.
- Attach the "question" label to your newly created issue.

We will then take care of the issue as soon as possible.

<!--
You might want to create a separate issue tag for questions and include it in this
description. People should then tag their issues accordingly.

Depending on how large the project is, you may want to outsource the questioning, e.
g. to Stack Overflow or Gitter. You may add additional contact and information
possibilities:
- IRC
- Slack
- Gitter
- Stack Overflow tag
- Blog
- FAQ
- Roadmap
- E-Mail List
- Forum
-->

## I Want To Contribute

> ### Legal Notice <!-- omit in toc -->
> When contributing to this project, you must agree that you have authored 100% of
> the content, that you have the necessary rights to the content and that the content
> you contribute may be provided under the project license.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information.
Therefore, we ask you to investigate carefully, collect information and describe the
issue in detail in your report. Please complete the following steps in advance to
help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side, e.g. using 
  incompatible environment components/versions (Make sure that you have read the 
  [documentation](https://hsbc.github.io/pyratings/). If you are looking for support,
  you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same 
  issue you are having, check if there is not already a bug report existing for your 
  bug or error in the
  [bug tracker](https://github.com/hsbc/pyratings/issues?q=label%3Abug).
- Collect information about the bug:
  - Stack trace (Traceback).
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM).
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, 
    depending on what seems relevant.
  - Possibly your input and the output.
  - Can you reliably reproduce the issue? And can you also reproduce it with older 
    versions?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including 
> sensitive information to the issue tracker, or elsewhere in public. Instead, 
> sensitive bugs must be sent by email to <opensource@hsbc.com>.
<!-- You may add a PGP key to allow the messages to be sent encrypted as well. -->

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/hsbc/pyratings//issues/new). (Since we can't be 
  sure at this point whether it is a bug or not, we ask you not to talk about a bug 
  yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* 
  that someone else can follow to recreate the issue on their own. This usually 
  includes your code. For good bug reports, you should isolate the problem and create 
  a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there 
  are no reproduction steps or no obvious way to reproduce the issue, the team will 
  ask you for those steps and mark the issue as `needs-repro`. Bugs with the 
  `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well 
  as possibly other tags (such as `critical`), and the issue will be left to be 
  [implemented by someone](#your-first-code-contribution).

<!-- You might want to create an issue template for bugs and errors that can be used
as a guide and that defines the structure of the information to be included. If you
do so, reference it here in the description. -->


### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for _pyratings_,
**including completely new features and minor improvements to existing functionality**.
Following these guidelines will help maintainers and the community to understand your
suggestion and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](https://hsbc.github.io/pyratings/) carefully and find out 
  if the functionality is already covered.
- Perform a [search](https://github.com/hsbc/pyratings//issues) to see if the 
  enhancement has already been suggested. If it has, add a comment to the existing 
  issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to 
  you to make a strong case to convince the project's developers of the merits of 
  this feature.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as
[GitHub issues](https://github.com/hsbc/pyratings//issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Use **feat:** as a prefix, e.g. "feat: Add awesome enhancement".
- Provide a **step-by-step description of the suggested enhancement** in as many 
  details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see 
  instead** and why. At this point, you can also tell which alternatives do not work 
  for you.
- You may want to **include screenshots and animated GIFs** which help you 
  demonstrate the steps or point out the part which the suggestion is related to. 
- **Explain why this enhancement would be useful** to most _pyratings_ users. You may 
  also want to point out other projects that solved it better and which could serve 
  as inspiration.

<!-- You might want to create an issue template for enhancement suggestions that can 
be used as a guide and that defines the structure of the information to be included. 
If you do so, reference it here in the description. -->

### Your First Code Contribution

GitHub provides a good [introduction](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) on how to contribute to an open source project. In a nutshell, the process involves the following steps:

1. Fork (i.e. copy) the repository to your own GitHub account.
2. Clone the fork to your local machine.
3. Create a new branch to work on.
4. Commit and push your changes to your own GitHub.
5. Create the Pull Request.

<!-- omit in toc -->
#### How do I set up my dev environment?

- _pyratings_ requires Python 3.9 at a minimum.
- Clone the fork to your local machine.
- Create a virtual environment.

```shell
python -m venv .venv
```
  
- Activate your virtual environment.

```shell
source ./.venv/Scripts/activate  # bash 
```

```shell
./.venv/Scripts/activate  # Windows 
```
  
- Install _pyratings_ in editable mode (including all development dependencies).<br>
  _pyratings_ is using ``pyproject.toml`` as configuration file. In order to install 
  the package in editable mode, make sure you have ``pip>=21.3`` installed on your 
  machine.

```shell
python -m pip install --upgrade pip  # upgrading pip to latest version
```

```shell
pip install --upgrade -e .[dev,docs,tests]  # install pyratings in editable mode
```

The _pyratings_ package adheres to a bunch of [Style guides](#style-guides), that 
will be enforced with the help of [Pre-commit](https://pre-commit.com/). 

#### Further dev setup and what I need to now about "pre-commit"

Before you commit your code changes, you should make sure, that you only commit code 
that is of good quality and adheres to the projects [Style guides](#style-guides).  
``pre-commit`` hooks run all the auto-formatters, linters, and other quality checks to
make sure the changeset is in good shape before a commit/push happens. If it finds 
any issues with your code, ``pre-commit`` will prevent the actual commit. You then 
have the chance to fix all issues and re-commit your code changes. 

In concrete, besides ``pre-commit``'s native checks, the following hooks have been 
implemented (in alphabetical order):

* [autoflake](https://pypi.org/project/autoflake/): Removes unused imports and
  unused variables from Python code.
* [black](https://pypi.org/project/black/): The Uncompromising Code Formatter
* [flake8](https://pypi.org/project/flake8/): Flake8 is a Python library that
  wraps ``PyFlakes``, ``pycodestyle`` and Ned Batchelder's McCabe script. It is a
  great toolkit for checking your code base against coding style (PEP8), programming
  errors and to check cyclomatic complexity.
* [flake8-annotations](https://pypi.org/project/flke8ake8-annotations/): Detects the
  absence of PEP 3107-style function annotations and PEP 484-style type comments.
* [flake8-bandit](https://pypi.org/project/flake8-bandit/): Automated security
  testing.
* [flake8-black](https://pypi.org/project/flake8-black/): Validating Python code
  style with the command line code formatting tool black.
* [flake8-bugbear](https://pypi.org/search/?q=flake8-bugbear): Finding likely
  bugs and design problems in your program.
* [flake8-builtins](https://pypi.org/project/flake8-builtins/): Check for python
  builtins being used as variables or parameters.
* [flake8-comprehensions](https://pypi.org/search/?q=flake8-comprehensions):
  Helps you write a better list/set/dict comprehensions.
* [flake8-docstrings](https://pypi.org/project/flake8-docstrings/): Check docstrings.
* [flake8-eradicate](https://pypi.org/project/flake8-eradicate/): Find commented
  out (or so-called "dead") code.
* [isort](https://pypi.org/project/isort/): Sort imports alphabetically, and
  automatically separated into sections and by type.
* [pep8-naming](https://pypi.org/project/pep8-naming/): Check your code against
  PEP 8 naming conventions.

You can install the hooks with (runs for each commit):

```shell
pre-commit install
```

Or if you want them to run only for each push:

```shell
pre-commit install -t pre-push
```

Or if you want to run all checks manually for all files:

```shell
pre-commit run --all-files
```


<!-- omit in toc -->
#### How do I execute unit tests?

Running simple unit tests using ``pytest`` is as easy as
```shell
pytest
```

In addition, you can perform more rigorous linting and tests against multiple Python
versions. In this case, the test result depends on the Python versions available on 
your machine. Make sure you've got at least Python 3.9 installed on your machine. 
Then simply run:
```shell
nox
```
If all tests pass, you should get a result comparable to this:
```shell
nox > Ran multiple sessions:
nox > pre-commit: success
nox > * tests-3.9: success
nox > * tests-3.10: success
nox > * tests-3.11: success
```

### Improving The Documentation

The documentation is completely written in _Markdown_. Utilizing the
[mkdocs](https://www.mkdocs.org/) and [mkdocstrings](https://mkdocstrings.github.io/)
libraries, the content will be generated automatically from the **docs** directory 
and from the docstrings of the public signatures of the source code.

There is always room for improvement. So, if you feel something isn't as clear 
described as it should be, please don't hesitate to open an 
[Issue](https://github.com/hsbc/pyratings/issues/new). Also, please attach the 
**documentation** label to it in order to make the maintainers' life a bit easier.

## Style guides

### Code formatting

This project uses the [black](https://black.readthedocs.io/) formatter to 
automatically format the code basis. The line length has been set to 88 characters.

### Linting

We use [flake8](https://pypi.org/project/flake8/) as our tool of choice for style 
guide enforcement. That means, contributers should adhere to the following points 
(not exhaustive):

- Every module must have a docstring to describe what the module is all about.
- Every function signature should have type hints as well as return values.
- Every function must have a docstring in
  [numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

### Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/)
specification. This will help us to automatically generate the
[CHANGELOG](https://hsbc.github.io/pyratings/changelog/).

## Attribution
This guide is based on the **contributing-gen**.
[Make your own](https://github.com/bttger/contributing-gen)!
