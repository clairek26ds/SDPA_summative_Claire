import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):
    """Test ingredient losses, weekly accounting and bankruptcy conditions."""

    def test_discarding_ingredients(self):
        """Verify that ingredient losses are calculated and rounded upwards correctly."""
        # checking the amount of discard
        stock1 = Stock()
        remaining1 = {"flour": 105, "butter": 105, "fruit": 105}
        expected1 = {"flour": 0, "butter": 11, "fruit": 21}

        self.assertEqual(stock1.discarded(remaining1), expected1)

    def test_discarding_small_amountof_ingredients(self):
        """veryfy that loss rounding is caculated correctly for small quantity"""
        # checking small number of discard
        stock2 = Stock()
        remaining2 = {"flour": 1, "butter": 1, "fruit": 1}
        expected2 = {"flour": 0, "butter": 1, "fruit": 1}

        self.assertEqual(stock2.discarded(remaining2), expected2)

    def test_closing_cash_for_no_sales(self):
        """veryfy that wages, rent, and closing cash on a week without sale is calculated correctly"""
        bakery1 = Bakery()
        decision1 = {
            "workforce": 1,
            "sales":{"loaf":0, "bun":0, "slice":0},
            "purchases":{"flour":0, "butter":0, "fruit":0}
        }
        demand1 = {"loaf":1, "bun":0, "slice":0}

        expected_wage = 10000
        expected_rent = 5000
        expected_closing_cash  = 85000
        # 100000 initial cash + 0 revenue - 10000 wages - 5000 rent - 0 purcahse = 85000

        record = bakery1.step(decision1, demand1)
        # checking whether week of no sales returns valid account state
        self.assertEqual(record["closing_cash"], expected_closing_cash)
        self.assertEqual(record["wages"], expected_wage)
        self.assertEqual(record["rent"], expected_rent)

    def test_if_cash_zero_bankrupt(self):
        """Verify that reaching zero cash after trading does not cause bankruptcy"""
        # test1: getting zero cash after Bakery.step()
        bakery1 = Bakery(initial_cash=15000)
        decision1 = {
            "workforce": 1,
            "sales":{"loaf":0, "bun":0, "slice":0},
            "purchases":{"flour":0, "butter":0, "fruit":0}
        }
        demand1 = {"loaf":1, "bun":0, "slice":0}

        bakery1.step(decision1, demand1)
        # test1: checking bankrupcy, cash state, model running state after Bakery.step()
        self.assertEqual(bakery1.bankrupt, False)
        self.assertEqual(bakery1.get_cash(), 0)
        self.assertFalse(bakery1.is_stopped())

    def test_if_cash_zero_start_bankrupt(self):
        """Verify that zero initial cash does not cause bankruptcy"""
        # test2: starting from cash 0
        bakery2 = Bakery(initial_cash=0)
        # test2: checking bankrupcy, cash state, model running state after Bakery.step()
        self.assertEqual(bakery2.bankrupt, False)
        self.assertEqual(bakery2.get_cash(), 0)
        self.assertFalse(bakery2.is_stopped())

    def test_boundary_bankrupcy(self):
        """Verify that a negative cash balance of one penny(boundary) causes bankruptcy"""
        # test3: boundary check
        bakery3 = Bakery(initial_cash=14999)
        decision3 = {"workforce": 1,
                     "sales":{"loaf":0, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand3 = {"loaf":1, "bun":0, "slice":0}

        bakery3.step(decision3, demand3)
        # test3: checking bankrupcy, cash state, model running statenafter Bakery.step()
        self.assertEqual(bakery3.bankrupt, True)
        self.assertEqual(bakery3.get_cash(), -1)
        self.assertTrue(bakery3.is_stopped())

    def test_overall_accounting(self):
        """Verify weekly revenue, cash, labour usage and closing stock calculations"""
        bakery = Bakery()

        decision = {
            "workforce": 1,
            "sales": {"loaf": 1, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand = {"loaf": 1, "bun": 0, "slice": 0}

        expected_stock = {"flour": 996, "butter": 360, "fruit": 320}

        record = bakery.step(decision, demand)

        self.assertEqual(record["revenue"], 350)
        self.assertEqual(record["closing_cash"], 85350)
        self.assertEqual(record["minutes_used"], 6)
        self.assertEqual(record["closing_stock"], expected_stock)
        self.assertEqual(bakery.get_stock(), expected_stock)
        self.assertEqual(record["wages"], 10000)
        self.assertEqual(record["rent"], 5000)
        self.assertEqual(record["purchases_cost"], 0)

    def test_consecutive_weeks(self):
        """Verify that cash, stock and week numbers carry forward correctly between weeks"""
        bakery = Bakery()

        decision = {
            "workforce": 1,
            "sales": {"loaf": 1, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand = {"loaf": 1, "bun": 0, "slice": 0}

        # week1
        record1 = bakery.step(decision, demand)
        # week2
        record2 = bakery.step(decision, demand)

        # checking whether the record of former week is connected to the next week and cumulated
        self.assertEqual(record1["closing_cash"], record2["opening_cash"])
        self.assertEqual(record1["closing_stock"], record2["opening_stock"])
        self.assertEqual(record1["week"]+1, record2["week"])
        self.assertEqual(len(bakery.get_history()), 2)

        # checking whether the accounting itself is correct
        self.assertEqual(record2["closing_cash"], 70700)
        self.assertEqual(record2["closing_stock"], {"flour": 992, "butter": 324, "fruit": 256})
        self.assertEqual(bakery.week, 3)