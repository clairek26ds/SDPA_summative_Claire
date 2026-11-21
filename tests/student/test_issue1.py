import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):
    """Test stock independence and historical stock records"""

    def test_history_closing_stock(self):
        """verifying later trading weeks do not alter previous closing records"""
        bakery = Bakery()

        decision = {
                "workforce": 1,
                "sales":{"loaf":1, "bun":0, "slice":0},
                "purchases":{"flour":0, "butter":0, "fruit":0}
        }
        demand = {"loaf":1, "bun":0, "slice":0}
        week1 = bakery.step(decision, demand)

        # saving the original closing stock snapshot
        original_closing_stock = bakery.get_history()[0]["closing_stock"].copy()

        week2 = bakery.step(decision, demand)

        # check that Week1 closing stock has not changed
        self.assertEqual(bakery.get_history()[0]["closing_stock"], original_closing_stock)


    def test_sharing_stock_update_function(self):
        """verify that updating one Stock object doesn't affect another"""
        initial_stock = {i: n.capacity for i, n in INGREDIENTS.items()}

        # test1 (comparing direct stock update results)
        b1_stock = Stock()
        remaining = {"flour": 500, "butter": 200, "fruit": 100}
        b1_stock.update(remaining)

        # test1: Creating a new bakery which is supposed to have a initial full stock
        b2_stock = Stock()
        self.assertEqual(b2_stock.quantities, initial_stock)

        # test1: stock update of the first object should not change the second
        self.assertNotEqual(b1_stock.quantities, b2_stock.quantities)

    def test_sharing_stock_step_function(self):
        """Verify that trading in one bakery doesn't change the stock of another one"""
        initial_stock = {i: n.capacity for i, n in INGREDIENTS.items()}
        
        # test2 (comparing stock update through step function)
        bakery3 = Bakery()
        decision = {
                "workforce": 1,
                "sales":{"loaf":1, "bun":0, "slice":0},
                "purchases":{"flour":0, "butter":0, "fruit":0}
        }
        demand = {"loaf":1, "bun":0, "slice":0}
        bakery3.step(decision, demand)

        # test2: Creating a new bakery which is supposed to have a initial full stock
        bakery4 = Bakery()
        self.assertEqual(bakery4.get_stock(), initial_stock)

        # test2: stock change of bakery3 from Bakery.step() doens't affect bakery4
        self.assertNotEqual(bakery3.get_stock(), bakery4.get_stock())
