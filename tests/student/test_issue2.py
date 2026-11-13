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
        initial_stock = {i: n.capacity for i, n in INGREDIENTS.items()}

        # decision to make more than stock ingredients
        decision1 = {"workforce": 1,
                     "sales": {"loaf": 400, "bun": 200, "slice": 100},
                     "purchases": {"flour": 0, "butter": 0, "fruit": 0}}
        demand1 = {"loaf": 100, "bun": 80, "slice": 60}

        too_much_bread = Bakery()

        # The object should still have full stock if the decision1 fails and doesn't run
        with self.assertRaises(ValueError):
            too_much_bread.step(decision1, demand1)

        self.assertEqual(too_much_bread.get_stock(), initial_stock)

    def test_purchase_exceeding_capacity(self):
        initial_stock = {i: n.capacity for i, n in INGREDIENTS.items()}

        # decision to make more than stock ingredients
        decision1 = {"workforce": 2,
                     "sales": {"loaf": 80, "bun": 60, "slice": 30},
                     "purchases": {"flour": 800, "butter": 300, "fruit": 300}}
        demand1 = {"loaf": 100, "bun": 80, "slice": 60}

        too_much_purchase = Bakery()

        # testing whether the rejected decision due to lack of capacity changes stocks
        with self.assertRaises(ValueError):
            too_much_purchase.step(decision1, demand1)

        self.assertEqual(too_much_purchase.get_stock(), initial_stock)       
