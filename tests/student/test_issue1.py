import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):
    def test_history_closing_stock(self):
        bakery = Bakery()

        decision1 = {"workforce": 1,
                     "sales":{"loaf":1, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand1 = {"loaf":1, "bun":0, "slice":0}
        week1_record = bakery.step(decision1, demand1)
        # saving the original closing stock
        original_closing_stock = dict(week1_record["closing_stock"])

        decision2 = {"workforce": 1,
                     "sales":{"loaf":1, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand2 = {"loaf":1, "bun":0, "slice":0}
        week2_record = bakery.step(decision2, demand2)

        # check that Week1 closing stock has not changed
        self.assertEqual(week1_record["closing_stock"], original_closing_stock)


    def test_sharing_stock(self):
        initial_stock = {i: n.capacity for i, n in INGREDIENTS.items()}

        b1_stock = Stock()
        remaining = {"flour": 500, "butter": 200, "fruit": 100}
        b1_stock.update(remaining)

        # Creating a new bakery which is supposed to have a initial full stock
        b2_stock = Stock()
        self.assertEqual(b2_stock.quantities, initial_stock)

        # Changing the first object should not change the second
        self.assertNotEqual(b1_stock.quantities, b2_stock.quantities)

