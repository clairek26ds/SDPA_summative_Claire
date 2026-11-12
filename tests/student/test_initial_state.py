import unittest

from bakery import Bakery


class InitialStateTests(unittest.TestCase):
    def test_custom_starting_cash(self):
        # Arrange: choose an explicit starting value, in pence.
        bakery = Bakery(duration=1, initial_cash=12345)

        # Assert: construction should retain the value we supplied.
        self.assertEqual(bakery.get_cash(), 12345)

    def test_negative_starting_cash_is_rejected(self):
        # Arrange: the constructor requires non-negative starting cash.
        invalid_cash = -1

        # Act and assert: this construction must raise ValueError.
        with self.assertRaises(ValueError):
            Bakery(duration=1, initial_cash=invalid_cash)