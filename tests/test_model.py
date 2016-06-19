# -*- coding: utf-8 -*-
"""Tests for habito models."""

from unittest import TestCase
from sure import expect

import habito.model as model


class ModelTests(TestCase):
    def test_setup_creates_tables(self):
        model.setup(":memory:")

        expect(len(model.db.get_tables())).to.be(2)
