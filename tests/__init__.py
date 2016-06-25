# -*- coding: utf-8 -*-
"""Base test case for habito."""

from datetime import datetime
from unittest import TestCase
from habito.models import HabitModel, ActivityModel


class HabitoTestCase(TestCase):
    """Base test case class for habito tests."""

    def create_habit(self, name="Habit 1", created_date=datetime.now(),
                     quantum=0, magica="be awesome!"):
        habit = HabitModel.create(name=name,
                                  created_date=created_date,
                                  quantum=quantum,
                                  units="dummy_units",
                                  magica=magica)
        return habit

    def add_activity(self, habit, quantum=0.0, update_date=datetime.now()):
        activity = ActivityModel.create(for_habit=habit,
                                        quantum=quantum,
                                        update_date=update_date)
        return activity
