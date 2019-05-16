Securing Flask Accounts with Two Factor Authentication using `TOTP`_
=====

Setup
----------

.. code-block:: text

    $ git clone https://github.com/henriquesgabriel/flask-2fa.git
    $ cd flask-2fa
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

Run
----------

.. code-block:: text

    $ export FLASK_APP=login
    $ export FLASK_ENV=development
    $ flask run

.. _TOTP: https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm
