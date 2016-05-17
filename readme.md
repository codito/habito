# Habito `1.0a2`
Simple commandline habits tracker.

[![Linux Build Status](https://img.shields.io/travis/codito/habito.svg)](https://travis-ci.org/codito/habito)
[![Windows Build status](https://img.shields.io/appveyor/ci/codito/habito.svg)](https://ci.appveyor.com/project/codito/habito)
[![codecov coverage](https://img.shields.io/codecov/c/github/codito/habito.svg)](http://codecov.io/github/codito/habito?branch=master)
[![PyPI](https://img.shields.io/pypi/dm/habito.svg)](https://pypi.python.org/pypi/habito)


# Installation

    pip install habito

# Usage
Here's how a command line session looks like:

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

# Screenshot
![Habito screenshot](http://i.imgur.com/w6K57Bl.jpg)

# Roadmap
Some of the stuff on top of my mind:

* `habito list` can be better. It doesn't check if tables can be output in
terminal screen appropriately :(
* Show how much data is needed to get me on track to meet goals
* Gamification!

# Contribute
`habito` is alpha at the moment. Please try it out and file any issues at github
issues page. Your patches are welcome!
