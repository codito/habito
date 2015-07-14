# Habito `1.0a1`
Simple commandline habits tracker.

[![Build Status](https://drone.io/github.com/codito/habito/status.png)](https://drone.io/github.com/codito/habito/latest)

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
