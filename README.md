# ARORA

[![Build Status](https://github.com/Jannetty/PythonRootDevModel/workflows/build/badge.svg)](https://github.com/Jannetty/PythonRootDevModel/actions?query=workflow%3Abuild)
[![Codecov](https://codecov.io/gh/Jannetty/PythonRootDevModel/branch/main/graph/badge.svg?token=SRGlpwpsbr)](https://codecov.io/gh/Jannetty/PythonRootDevModel)
![Lint Status](https://github.com/Jannetty/PythonRootDevModel/actions/workflows/lint.yml/badge.svg)
![Documentation](https://github.com/Jannetty/PythonRootDevModel/actions/workflows/documentation.yml/badge.svg)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

To direct biological systems towards specific desired objectives—such as shaping organ development or restoring health—we must first have a fundamental understanding of the cell decision processes underlying system behavior. 
Biological processes involve many molecular interactions across various spatial and temporal scales.
This complexity presents a substantial challenge: understanding how perturbations at the molecular and cellular levels affect overall system behavior. 

Agent-Based Models (ABMs) are a powerful tool for interrogating how changes in cellular decision making and perturbations in cell processes affect the emergent behavior of complex biological systems ([Prybutok et al. 2022](https://www.sciencedirect.com/science/article/abs/pii/S0958166922000313), [Yu and Bagheri 2016](https://pubmed.ncbi.nlm.nih.gov/27115496/)).
In ABMs, agents—here representing individual cells—follow predefined rules dictating their behavior as they progress through time and interact with other agents and their environment.  
These rules are derived from hypothesized or observed relationships between low-level interactions and emergent behavior in the system, thus enabling highly interpretable exploration of how changes or perturbations at the agent level affect system dynamics and system-wide emergent behavior.
ABMs have been effective at interrogating complex bioprocesses ([Reisfeld et al. 2013](https://www.nature.com/articles/s41598-021-04205-8), [Prybutok et al. 2022](https://pubmed.ncbi.nlm.nih.gov/35903149/), [Yu and Bagheri 2020](https://pubmed.ncbi.nlm.nih.gov/32596213/), [Yu and Bagheri 2021](https://pubmed.ncbi.nlm.nih.gov/34139155/)).
Here I am constructing an ABM of lateral root development---the process by which new lateral roots emerge from the primary root of dicot plants---with the goal of identifying methods for controlling the timing and locations of lateral root emergence, ultimately enabling precise manipulation of dicot root architecture.

This project is a work in progress.

This repository uses the following tools:

- Github Actions for CI
- [Poetry](https://python-poetry.org/) for packaging and dependency management
- [Tox](https://tox.readthedocs.io/en/latest/) for automated testing
- [Black](https://black.readthedocs.io/en/stable/) for code formatting
- [Pylint](https://www.pylint.org/) for linting
- [Mypy](http://mypy-lang.org/) for type checking
- [Sphinx](https://www.sphinx-doc.org/) for automated documentation
