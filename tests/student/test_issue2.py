import unittest
from bakery import Bakery
from stock import Stock
from ingredient import INGREDIENTS

class TestIssue(unittest.TestCase):
    def test_rejected_decision_changing_stocks(self):
        too_much_bread = Bakery(initial_stock={"flour": 10, "butter": 10, "fruit": 10})
        # making copy of initial states
        initial_stock = too_much_bread.get_stock().copy()
        initial_cash = too_much_bread.get_cash()
        initial_week = too_much_bread.week
        initial_history = too_much_bread.get_history()

        # decision to make more than stock ingredients
        decision1 = {"workforce": 1,
                     "sales": {"loaf": 2, "bun": 2, "slice": 1},
                     "purchases": {"flour": 0, "butter": 0, "fruit": 0}}
        demand1 = {"loaf": 10, "bun": 10, "slice": 10}

        # testing whether the rejected decision due to lack of ingredients changes bakery state
        with self.assertRaises(ValueError):
            too_much_bread.step(decision1, demand1)

        self.assertEqual(too_much_bread.get_stock(), initial_stock)
        self.assertEqual(too_much_bread.get_cash(), initial_cash)
        self.assertEqual(too_much_bread.week, initial_week)
        self.assertEqual(too_much_bread.get_history(), initial_history)

    def test_purchase_exceeding_capacity(self):
        too_much_purchase = Bakery()
        # making copy of initial states
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
        # making copy of initial states
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

    def test_after_rejected_decision(self):
        decision_over_demand = Bakery()
        
        initial_stock = decision_over_demand.get_stock().copy()
        initial_cash = decision_over_demand.get_cash()
        initial_week = decision_over_demand.week
        initial_history = decision_over_demand.get_history()

        # decision to produce more than demand
        decision1 = {"workforce": 2,
                     "sales": {"loaf": 50, "bun": 20, "slice": 30},
                     "purchases": {"flour": 0, "butter": 0, "fruit": 0}}
        demand1 = {"loaf": 20, "bun": 30, "slice": 10}

        # testing whether the rejected decision due to make more than demand changes bakery state
        with self.assertRaises(ValueError):
            decision_over_demand.step(decision1, demand1)

        self.assertEqual(decision_over_demand.get_stock(), initial_stock)
        self.assertEqual(decision_over_demand.get_cash(), initial_cash)
        self.assertEqual(decision_over_demand.week, initial_week)       
        self.assertEqual(decision_over_demand.get_history(), initial_history)       

        # valid decision
        decision2 = {"workforce": 1,
                     "sales": {"loaf": 10, "bun": 10, "slice": 10},
                     "purchases": {"flour": 0, "butter": 0, "fruit": 0}}
        demand2 = {"loaf": 20, "bun": 30, "slice": 10}

        expected_stock = {"flour": 920, "butter": 342, "fruit": 304}
        # ingredients, discard, purchase
        expected_cash = 95000
        # 100000 initial cash + 10000 revenue - 10000 wages - 5000 rent - 0 purcahse = 95000

        # testing whether valid decision following rejected one works correctly
        record = decision_over_demand.step(decision2, demand2)
    
        self.assertEqual(record["closing_stock"], expected_stock)
        self.assertEqual(record["closing_cash"], expected_cash)
        self.assertEqual(record["week"], 1)    
        self.assertEqual(len(decision_over_demand.get_history()), 1)       
