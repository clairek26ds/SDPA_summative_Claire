import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):
    def test_history_closing_stock(self):
        bakery = Bakery()

        decision = {"workforce": 1,
                     "sales":{"loaf":1, "bun":0, "slice":0},
                     "purchases":{"flour":0, "butter":0, "fruit":0}}
        demand = {"loaf":1, "bun":0, "slice":0}
        week1 = bakery.step(decision, demand)

        # saving the original closing stock snapshot
        original_closing_stock = bakery.get_history()[0]["closing_stock"].copy()

        week2 = bakery.step(decision, demand)

        # check that Week1 closing stock has not changed
        self.assertEqual(bakery.get_history()[0]["closing_stock"], original_closing_stock)


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
