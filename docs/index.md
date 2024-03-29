# Habito

Simple command line habits tracker.

[![Version](https://img.shields.io/pypi/v/habito.svg)](https://pypi.python.org/pypi/habito)
[![License](https://img.shields.io/github/license/codito/habito.svg)](https://github.com/codito/habito/blob/master/LICENSE.md)

<script src="https://asciinema.org/a/sczj9UFocJ6VbWLGWBguc1XCI.js" id="asciicast-sczj9UFocJ6VbWLGWBguc1XCI" async></script>

---

## Installation

Habito requires `python 3.10+` to be available in the system. You can install
`habito` like any other python package.

```shell
# Install pipx if needed: `pip install pipx`
# Ensure ~/.local/bin is available in system PATH
pipx install habito
```

Habito is packaged for following operating systems. Please use the OS specific
package manager to install it.

- Archlinux: [habito AUR package][habito-aur]

[habito-aur]: https://aur.archlinux.org/packages/habito/

### Upgrade to latest version

If you use `pipx` based approach, please use following command line to upgrade
`habito` to latest version.

```shell
pipx upgrade habito
```

Use OS specific instructions to upgrade otherwise. For example, Arch Linux users
may use any AUR wrapper like `yay`.

```shell
yay -Syu habito
```

## Quickstart

Let's get started with a classic `habito` flow.

### Add a habit

There are a few details to contemplate upon before you create a habit.

- A one or two word name for the habit. E.g. writing
- A measurable unit. E.g. words
- A daily goal. E.g. 750

You can add the habit now.

```shell
$ habito add writing 750 -u words

You have commited to 750.0 words of writing every day!
```

### List habits

You can see the habits tracked by habito using the `list` command.

```shell
$ habito list

┌───────────────────────┬───────┬────────┬──────────────────────────┐
│ Habit                 │ Goal  │ Streak │ Activities               │
├───────────────────────┼───────┼────────┼──────────────────────────┤
│ 1: writing            │ 750.0 │ 0 days │ □ □ □ □ □ □ □ □ □ □ □ □  │
└───────────────────────┴───────┴────────┴──────────────────────────┘
```

It shows the **goal** for tracked habit, and the progress for past few days. A
`□` symbol indicates goal is _not met_ for that day.

### Daily check-in

Let's update progress for today.

```shell
> habito checkin writing -q 800

Added 800.0 words to habit writing for Sat Feb 17 2018.

> habito list

┌───────────────────────┬───────┬────────┬──────────────────────────┐
│ Habit                 │ Goal  │ Streak │ Activities               │
├───────────────────────┼───────┼────────┼──────────────────────────┤
│ 1: writing            │ 750.0 │ 1 day  │ ■ □ □ □ □ □ □ □ □ □ □ □  │
└───────────────────────┴───────┴────────┴──────────────────────────┘
```

With the latest `checkin`, we have a green colored square <span
style="color:green">■</span> for the day. It indicates we have met the goal for
that day!

Go ahead and add a few habits. Try a few check-ins. Did you know it is possible
to check-in for a past date? And you can `delete` the test habit later.

Head over to the [Commands](commands.md) reference page for more details of each
command.
