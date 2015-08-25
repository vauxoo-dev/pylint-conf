THIS MODULE IS DEPRECATED HERE.
YOU CAN GO TO https://github.com/OCA/maintainer-tools/pull/105

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Autopep8 Extended
=================

This script overwrite with monkey patch the original script of [autopep8](https://github.com/hhatto/autopep8)
to support custom refactory of code.

* List of errors added:
  
  - `CW0001` Named of class has snake_case style, should use CamelCase.

Installation
============

To install this module, you need to:

* Install [autopep8](https://pypi.python.org/pypi/autopep8) with
  `pip install --upgrade autopep8`

* Download the repository: https://github.com/Vauxoo/pylint-conf
  `git clone https://github.com/Vauxoo/pylint-conf`

Configuration
=============

To configure this module, you need to:

* Add to `PATH` your recent repository downloaded with folder YOUR_REPO_PATH/autopep8_extended
  `export PATH=${PATH}:YOUR_REPO_PATH/autopep8_extended`

Usage
=====

To use this module, you need to:

* Run the command `autopep8_extended.py YOUR_CODE_PATH`

Known issues / Roadmap
======================

* Currently just work with `snake_case to CamelCase` script.
* I hope to add more refactory cases


Credits
=======

Contributors
------------

* Moises Lopez <moylop260@vauxoo.com>
