import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

# INGREDIENTS = {
#     "flour": Ingredient(1000, 10, 0),
#     "butter": Ingredient(400, 20, 10),
#     "fruit": Ingredient(400, 15, 20),
# }

# PRODUCTS = {
#     "loaf": Product([RecipeItem(INGREDIENTS["flour"], 4)], 6, 350),
#     "bun": Product([RecipeItem(INGREDIENTS["flour"], 2),
#                     RecipeItem(INGREDIENTS["butter"], 1)], 4, 250),
#     "slice": Product([RecipeItem(INGREDIENTS["flour"], 2),
#                       RecipeItem(INGREDIENTS["butter"], 1),
#                       RecipeItem(INGREDIENTS["fruit"], 2)], 5, 400),
# }

class TestIssue(unittest.TestCase):
    def test_rejected_decision_changing_stocks(self):
        too_much_bread = Bakery()
        initial_stock = too_much_bread.get_stock().copy()
        initial_cash = too_much_bread.get_cash()
        initial_week = too_much_bread.week
        initial_history = too_much_bread.get_history()

        # decision to make more than stock ingredients
        decision1 = {"workforce": 2,
                     "sales": {"loaf": 300, "bun": 200, "slice": 100},
                     "purchases": {"flour": 0, "butter": 0, "fruit": 0}}
        demand1 = {"loaf": 400, "bun": 300, "slice": 120}

        # testing whether the rejected decision due to lack of ingredients changes bakery state
        with self.assertRaises(ValueError):
            too_much_bread.step(decision1, demand1)

        self.assertEqual(too_much_bread.get_stock(), initial_stock)
        self.assertEqual(too_much_bread.get_cash(), initial_cash)
        self.assertEqual(too_much_bread.week, initial_week)
        self.assertEqual(too_much_bread.get_history(), initial_history)

    def test_purchase_exceeding_capacity(self):
        too_much_purchase = Bakery()

        initial_stock = too_much_purchase.get_stock().copy()
        initial_cash = too_much_purchase.get_cash()
        initial_week = too_much_purchase.week
        initial_history = too_much_purchase.get_history()

        # decision to buy more than stock capacity
        decision1 = {"workforce": 2,
                     "sales": {"loaf": 80, "bun": 60, "slice": 30},
                     "purchases": {"flour": 800, "butter": 300, "fruit": 300}}
        demand1 = {"loaf": 100, "bun": 80, "slice": 60}

        # testing whether the rejected decision due to lack of capacity changes bakery state
        with self.assertRaises(ValueError):
            too_much_purchase.step(decision1, demand1)

        self.assertEqual(too_much_purchase.get_stock(), initial_stock)
        self.assertEqual(too_much_purchase.get_cash(), initial_cash)
        self.assertEqual(too_much_purchase.week, initial_week)   
        self.assertEqual(too_much_purchase.get_history(), initial_history)

    def test_purchase_exceeding_budget(self):
        too_much_purchase = Bakery(initial_cash=1000)

        initial_stock = too_much_purchase.get_stock().copy()
        initial_cash = too_much_purchase.get_cash()
        initial_week = too_much_purchase.week
        initial_history = too_much_purchase.get_history()

        # decision to buy more than budget
        decision1 = {"workforce": 2,
                     "sales": {"loaf": 0, "bun": 100, "slice": 0},
                     "purchases": {"flour": 0, "butter": 100, "fruit": 0}}
        demand1 = {"loaf": 20, "bun": 200, "slice": 50}

        # testing whether the rejected decision due to purchase exceeding budget changes bakery state
        with self.assertRaises(ValueError):
            too_much_purchase.step(decision1, demand1)

        self.assertEqual(too_much_purchase.get_stock(), initial_stock)
        self.assertEqual(too_much_purchase.get_cash(), initial_cash)
        self.assertEqual(too_much_purchase.week, initial_week)       
        self.assertEqual(too_much_purchase.get_history(), initial_history)     