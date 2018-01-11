Habito
======

Simple commandline habits tracker.

|Linux Build Status| |Windows Build status| |codecov coverage| |PyPI|

Installation
============

::

    pip install habito

Archlinux users may install ``habito`` from AUR_.

.. _AUR: https://aur.archlinux.org/packages/habito/


Usage
=====

Here’s how a command line session looks like:

::

    $ # add a random habit
    $ habito add writing 200.0 --units words
    # output
    You have commited to 200.0 words of
    writing every day!

    $ # check in an update
    $ habito checkin writ --q 128.0
    # output
    Added 128.0 words to habit
    writing 

    $ # list status of habits
    $ habito list

Screenshot
==========

.. figure:: http://i.imgur.com/w6K57Bl.jpg
   :alt: Habito screenshot

   Habito screenshot

Roadmap
=======

Some of the stuff on top of my mind:

-  Show how much data is needed to get me on track to meet goals
-  Gamification!

Contribute
==========

``habito`` is alpha at the moment. Please try it out and file any issues
at github issues page. Your patches are welcome!

.. |Linux Build Status| image:: https://img.shields.io/travis/codito/habito.svg
   :target: https://travis-ci.org/codito/habito
.. |Windows Build status| image:: https://img.shields.io/appveyor/ci/codito/habito.svg
   :target: https://ci.appveyor.com/project/codito/habito
.. |codecov coverage| image:: https://img.shields.io/codecov/c/github/codito/habito.svg
   :target: http://codecov.io/github/codito/habito?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/habito.svg
   :target: https://pypi.python.org/pypi/habito

