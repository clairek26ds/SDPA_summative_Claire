import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):

    def test_discarding_ingredients(self):
        stock = Stock()

        remaining = {"flour": 105, "butter": 105, "fruit": 105}
        expected = {"flour": 0, "butter": 11, "fruit": 21}

        self.assertEqual(stock.discarded(remaining), expected)

    def test_closing_cash_for_no_sales(self):
        decision1 = {"workforce": 1,
                     "sales":{"loaf":0, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand1 = {"loaf":1, "bun":0, "slice":0}

        bakery = Bakery()
        expected_closing_cash  = (bakery.get_cash()
                                  - bakery.WEEKLY_RENT 
                                  - bakery.COST_PER_WORKER * decision1["workforce"]
                                  - sum(INGREDIENTS[k].price * decision1["purchases"][k] for k in INGREDIENTS))
        bakery.step(decision1, demand1)

        self.assertEqual(bakery.get_cash(), expected_closing_cash)

    def test_if_cash_zero_bankrupt(self):
        decision1 = {"workforce": 1,
                     "sales":{"loaf":0, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand1 = {"loaf":1, "bun":0, "slice":0}

        bakery = Bakery()
        bakery._cash = 15000
        bakery.step(decision1, demand1)

        self.assertEqual(bakery.bankrupt, False)