realt is a small Python library designed to make it easy to inspect the data
feed provided by the Government of Canada about votes in the House of Commons.

realt is coded for Python 2.7, though support may eventually extend to other
Python versions.

realt is released under the Apache License 2.0, see LICENSE.txt for details.

realt is tested against Python 2.7, installed using pip 7.1.0 and
setuptools 18.0.1. It is recommended that you do development in a virtualenv.

To install, or update dependencies, for development, run:

    $ pip install --no-deps --editable . --requirement requirements.txt

To package, for distribution, run:

    $ python setup.py sdist
