# Python project template repository

[![Build Status](https://github.com/bagherilab/python_project_template/workflows/build/badge.svg)](https://github.com/bagherilab/python_project_template/actions?query=workflow%3Abuild)
[![Codecov](https://img.shields.io/codecov/c/gh/bagherilab/python_project_template?token=HYF4KEB84L)](https://codecov.io/gh/bagherilab/python_project_template)
[![Lint Status](https://github.com/bagherilab/python_project_template/workflows/lint/badge.svg)](https://github.com/bagherilab/python_project_template/actions?query=workflow%3Alint)
[![Documentation](https://github.com/bagherilab/python_project_template/workflows/documentation/badge.svg)](https://bagherilab.github.io/python_project_template/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository is a template for Python projects that uses the GitHub Actions and the following tools:

- [Poetry](https://python-poetry.org/) for packaging and dependency management
- [Tox](https://tox.readthedocs.io/en/latest/) for automated testing
- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [Pylint](https://www.pylint.org/) for linting
- [Mypy](http://mypy-lang.org/) for type checking
- [Sphinx](https://www.sphinx-doc.org/) for automated documentation

Make sure you have Poetry installed.
The other tools will be installed by Poetry.


## Getting started

1. Clone the repo.
2. Initialize the repository (if you already have a `pyproject.toml` file, you can skip this step):

```bash
$ poetry init
```

3. Install dependencies.

```bash
$ poetry install
```

4. Activate the environment (this is all you need for day-to-day development):

```bash
$ poetry shell
```

5. Run the CLI.

```bash
$ python src/sandbox/cli.py 10
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
55
```

## General commands

The `Makefile` include three commands for working with the project.

- `make clean` will clean all the build and testing files
- `make build` will run tests, format, lint, and type check your code (you can also just run `tox`)
- `make docs` will generate documentation

## Template updates

There are a number of places in this template reposiotry that are specific to the template and will need to be updated for your specific project:

- Badge links in the `README.md`
- Section `[tool.poetry]` in `pyproject.toml`
- Project information section in `docs/conf.py`

## Repository tools

### Poetry

Poetry makes it explicit what dependencies (and what versions of those dependencies) are necessary for the project.
When new dependencies are added, Poetry performs an exhaustive dependency resolution to make sure that all the dependencies (and their versions) can work together.
This does mean the initial install can take a little while, especially if you have many dependencies, but subsequent installs will be faster once the `poetry.lock` file has been created.

To add a dependency, use:

```bash
$ poetry add <dependency>
```

You can additionally specify version constraints (e.g. `<dependency>@<version constraints>`).
Use `-D` to indicate development dependencies.
You can also add dependencies directly to the  file.

For projects with CLI, you can simplify the call to the CLI so instead of `python src/sandbox/cli.py 10` you can simply call `sandbox-cli 10`.
Add these commands to the `pyproject.toml` by linking a command and the method to call:

```toml
[tool.poetry.scripts]
sandbox-cli = "sandbox.cli:cli"
```

### GitHub Actions

Tests are run on each push.
For projects that should be tested on multiple Python versions, make sure to update the matrix with additional versions in `.github/workflows/build.yml`.

Documentation is automatically generated by `.github/workflows/documentation.yml` on pushes to the main branch.
The documentation files are deployed on a separate branch called `gh-pages`.
You can host the documentation using GitHub Pages (Settings > Pages) from this branch.

Linting is performed on each push.
This workflow `.github/workflows/lint.yml` lints code using Pylint (fails when score is < 7.0), checks formatting with Black (fails if files would be reformatted), and performs type checking with MyPy (fails if code has type errors).
Note that this type checking is not the same as the type checking done by Tox, which additionally checks for missing types.

### Tox

Tox aims to automate and standardize testing.
You can use tox to automatically run tests on different python versions, as well as things like linting and type checking.

Tox can be configured in `tox.ini` for additional python versions or testing environments.
Note that the type checking specified in the provided `tox.ini` is more strict than the type checking specified in `.github/workflows/lint.yml`.

You can run specific tox environments using:

```bash
$ tox -e <env>
```

### Pylint

Pylint checks for basic errors in your code, aims to enforce a coding standard, and identifies code smells.
The tool will score code out of 10, with the linting GitHub Action set to pass if the score is above 7.
Most recommendations from Pylint are good, but it is not perfect.
Make sure to be deliberate with which messages you ignore and which recommendations you follow.

Pylint can be configured in `.pylintrc` to ignore specific messages (such as `missing-module-docstring`), exclude certain variable names that Pylint considers too short, and adjust additional settings relevant for your project.

### Mypy

Mypy performs static type checking.
Adding type hinting makes it easier to find bugs and removes the need to add tests solely for type checking.

Mypy will avoid assuming types in imported dependencies, so will generally throw a `Cannot find implementation or library stub for module` error.
Update `mypy.ini` to ignore these missing imports:

```
[mypy-<dependency>.*]
ignore_missing_imports = True
```

Add a `py.typed` file to each module to indicate that the module is typed.

### Sphinx

Sphinx is a tool to generate documentation.
We have set it up to automatically generate documenation from [Numpy style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html).
It will also pull `README.md` into the main page.

Note that the documentation workflow `.github/workflows/documentation.yml` does not import dependencies, which will break the building process.
To avoid this, make sure to list your external dependencies in `conf.py` in the `autodoc_mock_imports` variable.

### Codecov

To use Codecov, you must set up the repo on [app.codecov.io](app.codecov.io) and add the code code token (`CODECOV_TOKEN`) as a repository secret.
Make sure to also up the badge token (not that same as the secret token!) in your README.
Coverage results from `.github/workflows/build.yml` will be automatically uploaded.
