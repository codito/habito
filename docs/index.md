# Habito

[![Build status](https://img.shields.io/travis/codito/habito.svg)](https://travis-ci.org/codito/habito)
[![Build status](https://img.shields.io/appveyor/ci/codito/habito.svg)](https://ci.appveyor.com/project/codito/habito)
[![Coverage](https://img.shields.io/codecov/c/github/codito/habito.svg)](http://codecov.io/github/codito/habito?branch=master)
[![Version](https://img.shields.io/pypi/v/habito.svg)](https://pypi.python.org/pypi/habito)
[![License](https://img.shields.io/github/license/codito/habito.svg)](https://github.com/codito/habito/blob/master/LICENSE.md)

Simple command line habits tracker.

TODO: screencast goes here!

---

## Installation

Habito requires `python 3.6+` to be available in the system. You can install
`habito` like any other python package.

```shell
pip install habito --user
```

If you prefer, remove the `--user` flag to install the package into systemwide
location.

Habito is packaged for following operating systems. Please use the OS specific
package manager to install it.

* Archlinux: [habito AUR package][habito-aur]

[habito-aur]: https://aur.archlinux.org/packages/habito/

### Upgrade to latest version

If you use `pip` based approach, please use following command line to upgrade
`habito` to latest version.

```shell
pip install habito --user --upgrade
```

Use OS specific instructions to upgrade otherwise. For example, Arch Linux users
may use any AUR wrapper like `yaourt`.

```shell
yaourt -Syu habito
```

## Quickstart

Let's get started with a classic `habito` flow.

### Add a habit

There are a few details to contemplate upon before you create a habit.

* A one or two word name for the habit. E.g. writing
* A measurable unit. E.g. words
* A daily goal. E.g. 750

You can add the habit now.

```shell
$ habito add writing 750 -u words

You have commited to 750.0 words of
writing every day!
```

### List habits

You can see the habits tracked by habito using the `list` command.

```shell
$ habito list

┌─────────┬───────┬─────────┬─────────┬─────────┬──────────┐
│ Habit   │ Goal  │ 1/12    │ 1/11    │ 1/10    │ 1/9      │
├─────────┼───────┼─────────┼─────────┼─────────┼──────────┤
│ writing │ 750.0 │ ✗ (0.0) │ ✗ (0.0) │ ✗ (0.0) │ ✗ (0.0)  │
└─────────┴───────┴─────────┴─────────┴─────────┴──────────┘
```

It shows the **goal** for tracked habit, and the progress for past few days. A
`✗` mark indicates goal is _not met_ for that day.

### Daily check-in

Let's update progress for today.

```shell
> habito checkin writing -q 800

Added 800 words to habit
writing

> habito list

┌─────────┬───────┬───────────┬─────────┬─────────┬─────────┐
│ Habit   │ Goal  │ 1/12      │ 1/11    │ 1/10    │ 1/9     │
├─────────┼───────┼───────────┼─────────┼─────────┼─────────┤
│ writing │ 750.0 │ ✓ (800.0) │ ✗ (0.0) │ ✗ (0.0) │ ✗ (0.0) │
└─────────┴───────┴───────────┴─────────┴─────────┴─────────┘
```

With the latest `checkin`, we have a `✓` for the day. It indicates we have met
the goal for that day!

Go ahead and add a few habits. Head over to the [Commands](commands.md)
reference page for more details of each command and usage.
