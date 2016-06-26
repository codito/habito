# -*- coding: utf-8 -*-
"""Base test case for habito."""

from datetime import datetime
from unittest import TestCase

import habito.models as models


class HabitoTestCase(TestCase):
    """Base test case class for habito tests."""

    def create_habit(self, name="Habit 1", created_date=datetime.now(),
                     quantum=0, magica="be awesome!"):
        habit = models.HabitModel.create(name=name,
                                         created_date=created_date,
                                         quantum=quantum,
                                         units="dummy_units",
                                         magica=magica)
        return habit

    def add_activity(self, habit, quantum=0.0, update_date=datetime.now()):
        activity = models.ActivityModel.create(for_habit=habit,
                                               quantum=quantum,
                                               update_date=update_date)
        return activity

    def add_summary(self, habit, target=0, target_date=datetime.now(),
                    streak=0):
        summary = models.Summary.create(for_habit=habit,
                                        target=target,
                                        target_date=target_date,
                                        streak=streak)
        return summary
