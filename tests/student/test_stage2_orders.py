import unittest
from bakery import Bakery
from replay import load_json, replay
from orderbook import OrderBook

class TestIssue(unittest.TestCase):
    """Test advance-order processing, decision rollback and Stage 1 compatibility"""
    def test_order_status_fulfilled(self):
        """verify successful order fulfillment and weekly counting"""
        # making valid order which is supposed to be fulfilled
        bakery = Bakery(
            orders = [
                {
                    "id": "A", 
                    "product_id": "loaf", 
                    "quantity": 3, 
                    "collection_week": 1
                }
            ]
        )
        order = bakery.order_book.orders[0]
        self.assertEqual(order.status, "pending")

       # valid decision and demand of the week
        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 10, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # testing whether the valid order results in fulfilled state
        bakery.step(decision1, demand1)
        record = bakery.get_history()[0]

        self.assertEqual(order.status, "fulfilled")
        self.assertEqual(record["fulfilled_order_ids"], ["A"])
        self.assertEqual(record["missed_order_ids"], [])
        self.assertEqual(record["order_revenue"], 1050)
        self.assertEqual(record["walk_in_revenue"], 3500) 
        self.assertEqual(record["revenue"], 4550)
        self.assertEqual(record["sales"]["loaf"], 10)
        # Check total flour consumed: (3 + 10) loaves × 4 flour
        self.assertEqual(record["consumed"]["flour"], 52)
        # Check total minutes used: (3 + 10) loaves × 6 minutes
        self.assertEqual(record["minutes_used"], 78)
        
                

    def test_order_status_missed(self):
        """verify unsuccessful order missed status and weekly counting"""
        # making invalid order (too much order which is supposed to be missed)
        bakery = Bakery(
            orders = [
                {
                    "id": "A", 
                    "product_id": "loaf", 
                    "quantity": 300, 
                    "collection_week": 1
                }
            ]
        )
        order = bakery.order_book.orders[0]
        self.assertEqual(order.status, "pending")

       # valid decision and demand of the week
        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 10, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # testing whether the invalid order results in missed state
        bakery.step(decision1, demand1)
        record = bakery.get_history()[0]

        self.assertEqual(order.status, "missed")
        self.assertEqual(record["fulfilled_order_ids"], [])
        self.assertEqual(record["missed_order_ids"], ["A"])
        self.assertEqual(record["order_revenue"], 0)
        self.assertEqual(record["walk_in_revenue"], 3500) 

    def test_multiple_due_orders_sorting(self):
        """verify that due orders are selected and sorted by ID"""
        # making orders which is not ascending by id
        records =[
            {
                "id": "D", 
                "product_id": "loaf", 
                "quantity": 1, 
                "collection_week": 3
            },
            {
                "id": "C", 
                "product_id": "loaf", 
                "quantity": 1, 
                "collection_week": 1
            },
            {
                "id": "A", 
                "product_id": "loaf", 
                "quantity": 1, 
                "collection_week": 2
            },
            {
                "id": "B", 
                "product_id": "loaf", 
                "quantity": 1, 
                "collection_week": 1
                }
        ]

        orderbook1 = OrderBook(records, duration = 6)
        # checking the initial order    
        order_ids = [o.id for o in orderbook1.orders]
        self.assertEqual(order_ids, ["D", "C", "A", "B"])
        # checking if it sorts correctly and brings the due orders only
        order_ids = [o.id for o in orderbook1.due_orders(1)]  
        self.assertEqual(order_ids, ["B", "C"])

    def test_multiple_orders_fulfilled_normally_after_missed(self):
        """verify that subsequent feasible order is fulfilled normally after a rejected one"""
        # making orders which will be fulfilled and missed one by one
        bakery = Bakery(
            orders = [
                {
                "id": "A", 
                "product_id": "loaf", 
                "quantity": 300, 
                "collection_week": 1},
                {
                "id": "B", 
                "product_id": "loaf", 
                "quantity": 1, 
                "collection_week": 1
                }
            ]
        )

        order_a = bakery.order_book.orders[0]
        order_b = bakery.order_book.orders[1]

        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 10, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # testing whether the valid order after missed order become fulfilled normally
        bakery.step(decision1, demand1)
        
        self.assertEqual(order_a.status, "missed")
        self.assertEqual(order_b.status, "fulfilled")
        self.assertEqual(bakery.get_history()[0]["fulfilled_order_ids"], ["B"])
        self.assertEqual(bakery.get_history()[0]["missed_order_ids"], ["A"])
        self.assertEqual(bakery.get_history()[0]["order_revenue"], 350)        


    def test_multiple_orders_processed_orderby_id(self):
        """verify that due orders are proceeded in ascending ID order with limited stock setting"""
        # making orders which is not ascending by id and stock which can fulfil only one
        bakery = Bakery(
            initial_stock={"flour": 6, "butter": 10, "fruit": 10},                        
            orders = [
                {
                    "id": "B", 
                    "product_id": "loaf", 
                    "quantity": 1, 
                    "collection_week": 1},
                {
                    "id": "A", 
                    "product_id": "loaf", 
                    "quantity": 1, 
                    "collection_week": 1
                }
            ]
        )

        order_b = bakery.order_book.orders[0]
        order_a = bakery.order_book.orders[1]

        # valid decision and demand of the week
        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 0, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # testing whether orders are fulfilled by id order
        bakery.step(decision1, demand1)
        record = bakery.get_history()[0]
        
        self.assertEqual(order_a.status, "fulfilled")
        self.assertEqual(order_b.status, "missed")
        self.assertEqual(record["fulfilled_order_ids"], ["A"])
        self.assertEqual(record["missed_order_ids"], ["B"])
        self.assertEqual(record["order_revenue"], 350)
        self.assertEqual(record["consumed"]["flour"], 4)       


    def test_rejected_due_to_purchase_rollback_to_initial(self):
        """verify that rejected purchase preserves bakery state and permits a retry"""
        # pre-order which can be fulfilled
        bakery = Bakery(
            orders = [
                {
                    "id": "A", 
                    "product_id": "loaf", 
                    "quantity": 1, 
                    "collection_week": 1
                }
            ]
        )
        order = bakery.order_book.orders[0]

        initial_cash = bakery.get_cash()
        initial_stock = dict(bakery.get_stock())
        initial_week = bakery.week
        initial_history = bakery.get_history()
        
        # too much purchase which will be rejected later in the step
        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 0, "bun": 0, "slice": 0},
            "purchases": {"flour": 10, "butter": 10, "fruit": 10}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        with self.assertRaises(ValueError):
            bakery.step(decision1, demand1)

        self.assertEqual(order.status, "pending")
        self.assertEqual(bakery.get_cash(), initial_cash)
        self.assertEqual(bakery.get_stock(), initial_stock)
        self.assertEqual(bakery.week, initial_week)
        self.assertEqual(bakery.get_history(), initial_history)

        # testing if the same order can be fulfilled if not rejected later
        decision2 = {
            "workforce": 1,
            "sales": {"loaf": 0, "bun": 0, "slice": 0},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand2 = {"loaf": 20, "bun": 10, "slice": 10}

        bakery.step(decision2, demand2)

        self.assertEqual(order.status, "fulfilled")
        self.assertEqual(bakery.week, 2)
        self.assertEqual(bakery.get_history()[0]["fulfilled_order_ids"], ["A"])
        self.assertEqual(bakery.get_history()[0]["week"], 1)
        self.assertEqual(len(bakery.get_history()), 1)
        self.assertEqual(bakery.get_cash(), 85350)
        # 100000 initial_cash - 10000 workforce - 5000 rent + 350 revenue_order

    def test_rejected_due_to_walkin_stock_shortage_rollback_to_initial(self):
        """verify that rejected walkin sale preserves the bakery state and rollback to initial stage"""
        # pre-order which can be fulfilled
        bakery = Bakery(
            initial_stock={"flour": 6, "butter": 10, "fruit": 10},
            orders = [
                {
                    "id": "A", 
                    "product_id": "loaf", 
                    "quantity": 1, 
                    "collection_week": 1
                }
            ]
        )
        order = bakery.order_book.orders[0]

        initial_cash = bakery.get_cash()
        initial_stock = dict(bakery.get_stock())
        initial_week = bakery.week
        initial_history = bakery.get_history()
        
        # make flour shortage after fulfiling order
        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 0, "bun": 0, "slice": 2}, 
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # check whether the rejected walkin sales rollback to the initial state
        with self.assertRaises(ValueError):
            bakery.step(decision1, demand1)

        self.assertEqual(order.status, "pending")
        self.assertEqual(bakery.get_cash(), initial_cash)
        self.assertEqual(bakery.get_stock(), initial_stock)
        self.assertEqual(bakery.week, initial_week)
        self.assertEqual(bakery.get_history(), initial_history)


    def test_no_orders(self):
        """veryfy normal trading without orders work corretly"""
        # Bakery with no order which is same as stage1 condition
        bakery = Bakery()
        # checking there is no order attributes
        self.assertEqual(bakery.order_book.orders, [])

        decision1 = {
            "workforce": 1,
            "sales": {"loaf": 0, "bun": 0, "slice": 10},
            "purchases": {"flour": 0, "butter": 0, "fruit": 0}
        }
        demand1 = {"loaf": 20, "bun": 10, "slice": 10}

        # cheching whether it makes results without pre-order as stage1 and if the revenue is the same as the revenue or walkin only
        bakery.step(decision1, demand1)
        record = bakery.get_history()[0]

        self.assertEqual(bakery.get_cash(), 89000)
        self.assertEqual(record["order_revenue"], 0)
        self.assertEqual(record["walk_in_revenue"], 4000)
        self.assertEqual(record["revenue"], record["walk_in_revenue"])
        self.assertEqual(record["sales"]["slice"], 10)
        self.assertEqual(record["fulfilled_order_ids"], [])
        self.assertEqual(record["missed_order_ids"], [])

    def test_no_orders_json(self):
        """veryfy normal trading without orders work corretly wtih json file test"""
        # running Bakery with no order with json file
        scenario = load_json("data/example.json")
        decisions = load_json("data/example_decisions.json")  

        bakery_record = replay(scenario, decisions)

        for record in bakery_record:
            self.assertEqual(record["fulfilled_order_ids"], [])
            self.assertEqual(record["missed_order_ids"], [])
            self.assertEqual(record["order_revenue"], 0)
            self.assertEqual(record["walk_in_revenue"], record["revenue"])