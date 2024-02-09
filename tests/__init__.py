# -*- coding: utf-8 -*-
"""Base test case for habito."""

from datetime import datetime, timedelta
from unittest import TestCase

import habito.models as models


class HabitoTestCase(TestCase):
    """Base test case class for habito tests."""

    one_day_ago = datetime.today() - timedelta(days=1)
    two_days_ago = datetime.today() - timedelta(days=2)
    three_days_ago = datetime.today() - timedelta(days=3)
    four_days_ago = datetime.today() - timedelta(days=4)

    def create_habit(
        self,
        name="HabitOne",
        created_date=datetime.now().date(),
        start_date=datetime.now().date(),
        active=True,
        quantum=0,
        frequency=1,
        minimize=False,
        magica="be awesome!",
    ):
        habit = models.Habit.create(
            name=name,
            created_date=created_date,
            start_date=start_date,
            quantum=quantum,
            active=active,
            units="dummy_units",
            frequency=frequency,
            minimize=minimize,
            magica=magica,
        )
        return habit

    def add_activity(self, habit, quantum=0.0, update_date=datetime.now()):
        activity = models.Activity.create(
            for_habit=habit, quantum=quantum, update_date=update_date
        )
        return activity

    def add_summary(self, habit, target=0, target_date=datetime.now(), streak=0):
        summary = models.Summary.create(
            for_habit=habit, target=target, target_date=target_date, streak=streak
        )
        return summary
