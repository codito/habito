from datetime import datetime, date, timedelta

import habito
from habito import models
from habito.commands import checkin
from tests.commands import HabitoCommandTestCase


class HabitoCheckinCommandTestCase(HabitoCommandTestCase):
    def test_habito_checkin_should_show_error_if_no_habit_exists(self):
        result = self._run_command(habito.commands.checkin,
                                   ["dummy habit", "-q 9.1"])

        assert result.exit_code == 0
        assert result.output.startswith("No habit matched the")

    def test_habito_checkin_should_show_error_if_name_is_empty(self):
        result = self._run_command(checkin)

        assert result.exit_code == 0
        assert result.output.startswith("No habit specified")

    def test_habito_checkin_should_show_error_if_multiple_habits_match(self):
        dummy_date = date(1201, 10, 12)
        habit = self.create_habit()
        habit_two = self.create_habit(name="Habit Two",
                                      created_date=dummy_date,
                                      quantum=0,
                                      magica="be awesome!")

        result = self._run_command(checkin,
                                   ["Habit", "-q 9.1"])

        assert result.exit_code == 0
        assert result.output.startswith("More than one habits matched the")

    def test_habito_checkin_should_add_data_for_a_habit(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units = "9.1 dummy_units"

        result = self._run_command(checkin,
                                   ["Habit", "-q 9.1"])
        activity_entry = models.Activity \
            .get(models.Activity.for_habit == habit)

        assert result.output.find(result_units) != -1
        assert result.output.find(habit.name) != -1
        assert activity_entry.quantum == 9.1

    def test_habito_checkin_should_skip_inactive_habit(self):
        habit = self.create_habit(active=False)
        self.add_summary(habit)
        result_units = "9.1 dummy_units"

        result = self._run_command(checkin,
                                   ["Habit", "-q 9.1"])

        activity_entry = models.Activity \
            .select().where(models.Activity.for_habit == habit)
        assert result.output.find(result_units) == -1
        assert result.output.find(habit.name) == -1
        assert activity_entry.count() == 0

    def test_habito_checkin_should_update_past_date(self):
        habit = self.create_habit()
        self.add_summary(habit)
        for i in range(5):
            d = datetime.now() - timedelta(days=i)
            date_str = "{d.month}/{d.day}".format(d=d).strip()
            checkin_result = self._run_command(checkin, ["Habit", "-d {}".format(date_str), "-q 35.0"])

            self._verify_checkin_date(date_str, d.year, checkin_result.output)
            assert "35.0 dummy_units" in checkin_result.output
        list_result = self._run_command(habito.commands.list, ["-l"])
        assert list_result.output.count("35") > 3

    def test_habito_checkin_should_update_past_year(self):
        habit = self.create_habit()
        self.add_summary(habit)
        d = datetime.now() + timedelta(days=2)
        date_str = "{d.month}/{d.day}".format(d=d).strip()

        checkin_result = self._run_command(checkin, ["Habit", "-d {}".format(date_str), "-q 35.0"])

        a = models.Activity.select() \
            .where(models.Activity.update_date.year == d.year-1).get()
        assert a.quantum == 35.0
        self._verify_checkin_date(date_str, d.year-1, checkin_result.output)
        assert "35.0 dummy_units" in checkin_result.output

    def test_habito_checkin_can_add_multiple_data_points_on_same_day(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units_one = "9.1 dummy_units"
        result_units_two = "10.0001 dummy_units"

        self._run_command(checkin, ["Habit", "-q 9.1"])
        result = self._run_command(checkin, ["Habit", "-q 10.0001"])

        activity_entry = models.Activity \
            .select().where(models.Activity.for_habit == habit)

        assert result.output.find(result_units_two) != -1
        assert result.output.find(habit.name) != -1
        assert activity_entry.count() == 2
        assert activity_entry[0].quantum == 9.1
        assert activity_entry[1].quantum == 10.0001

    def test_habito_checkin_asks_user_input_if_quantum_is_not_provided(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units_one = "9.1 dummy_units"

        # Pass \n to stdin to ensure prompt continues to appear until
        # a value is provided
        result = self._run_command_with_stdin(checkin, ["Habit"], "\n9.1")

        assert result.exit_code == 0
        assert result.output.find(result_units_one) != -1

    def test_habito_checkin_increments_streak_for_a_habit(self):
        habit = self.create_habit()
        self.add_activity(habit, update_date=self.one_day_ago)
        self.add_activity(habit, update_date=self.two_days_ago)
        self.add_summary(habit, streak=2)

        self._run_command(checkin, ["Habit", "-q 9.1"])

        assert models.Summary.get().streak == 3

    def test_habito_checkin_review_mode_iterates_all_habits(self):
        habit_one = self.create_habit()
        habit_two = self.create_habit(name="HabitTwo", quantum=2)
        habit_three = self.create_habit(name="HabitThree", active=False, quantum=2)
        self.add_summary(habit_one)
        self.add_summary(habit_two)
        self.add_summary(habit_three)

        result = self._run_command_with_stdin(checkin, ["--review"], "1.0\n2.0")

        activities = list(models.Activity.select())
        assert result.exit_code == 0
        assert len(activities) == 2
        assert activities[0].quantum == 1.0
        assert activities[1].quantum == 2.0

    def test_habito_checkin_review_mode_doesnt_update_default(self):
        habit = self.create_habit()
        self.add_summary(habit)

        result = self._run_command_with_stdin(checkin, ["-r"], "\n")

        assert result.exit_code == 0
        assert models.Activity.select().count() == 0

