"""Weekly trading calculations, independent of terminal input and output."""
from copy import deepcopy
from ingredient import INGREDIENTS
from product import PRODUCTS
from validation import integer, validate_decision
from stock import Stock
from orderbook import OrderBook


class Bakery:
    """A bounded simulation with stock, cash and completed weekly records."""
    # Fixed operating rates, in pence.
    WEEKLY_RENT = 5000
    COST_PER_WORKER = 10000

    def __init__(self, duration=6, initial_cash=100000, initial_stock=None, orders=None):
        self.duration = integer(duration, "duration", 1, 12)
        self._cash = integer(initial_cash, "initial_cash")
        self.stock = Stock(initial_stock)
        self.week = 1
        self.bankrupt = False
        self._history = []
        if orders is None:
            orders = []
        self.order_book = OrderBook(orders, self.duration)

    def can_fulfil(self, order, temp_stock, temp_minutes):
        """Whether current stock and minutes can fulfil the order"""
        product = PRODUCTS[order.product_id]
        consumed_each = {k: product.quantity_for(INGREDIENTS[k]) * order.quantity
                    for k in INGREDIENTS}
        minutes_each = product.minutes * order.quantity
        enough_stock = all(consumed_each[k] <= temp_stock.quantities[k] for k in INGREDIENTS)
        enough_time = minutes_each <= temp_minutes
        if enough_stock and enough_time:
            return consumed_each, minutes_each

    def get_stock(self):
        """Return the live stock dictionary; copy it to retain a snapshot."""
        return self.stock.quantities

    def get_cash(self):
        """Return the current cash balance in pence."""
        return self._cash

    def get_history(self):
        """Return independent record snapshots."""
        return deepcopy(self._history)

    def is_stopped(self):
        """Whether another trading week is forbidden."""
        return self.bankrupt or self.week > self.duration

    def step(self, decision, demand):
        """Validate and apply one complete week, returning a record dictionary."""
        if self.is_stopped():
            raise ValueError("simulation has stopped")
        workforce, sales, purchases = validate_decision(decision, demand)
        opening_stock = dict(self.stock.quantities)

        # temporary variable for stock update in case of rejection later
        temp_stock = deepcopy(self.stock)
        temp_minutes = workforce * 600

        sales_order = dict.fromkeys(PRODUCTS, 0)
        consumed_order = dict.fromkeys(INGREDIENTS, 0)
        minutes_order = 0
        fulfilled_order_ids = []
        missed_order_ids = []
        for order in self.order_book.due_orders(self.week):
            result = self.can_fulfil(order, temp_stock, temp_minutes)
            if result is None:
                missed_order_ids.append(order.id)
                continue
            consumed_each, minutes_each = result
            sales_order[order.product_id] += order.quantity
            for ingredient in INGREDIENTS:
                consumed_order[ingredient] += consumed_each[ingredient]
                temp_stock.quantities[ingredient] -= consumed_each[ingredient]
            minutes_order += minutes_each
            temp_minutes -= minutes_each
            fulfilled_order_ids.append(order.id)
        
        consumed_walkin = {k: sum(PRODUCTS[p].quantity_for(INGREDIENTS[k]) * sales[p] for p in PRODUCTS)
                    for k in INGREDIENTS}
        minutes_walkin = sum(PRODUCTS[p].minutes * sales[p] for p in PRODUCTS)
        # changed to compare dicisions with the overall amount of ingredients required rather than with individual products
        if any(consumed_walkin[k] > temp_stock.quantities[k] for k in INGREDIENTS):
            raise ValueError("insufficient ingredients")
        if minutes_walkin > temp_minutes:
            raise ValueError("insufficient labour")
        remaining = {k: temp_stock.quantities[k] - consumed_walkin[k] for k in INGREDIENTS}
        temp_stock.update(remaining)

        order_revenue = sum(PRODUCTS[p].price * sales_order[p] for p in PRODUCTS)
        walk_in_revenue = sum(PRODUCTS[p].price * sales[p] for p in PRODUCTS)
        revenue = order_revenue + walk_in_revenue
        consumed = {k: consumed_order[k] + consumed_walkin[k] for k in INGREDIENTS}
        minutes = minutes_order + minutes_walkin
        wages = workforce * self.COST_PER_WORKER
        rent = self.WEEKLY_RENT
        cash_after_charges = self._cash + revenue - wages - rent
        bankrupt = cash_after_charges < 0
        discarded = dict.fromkeys(INGREDIENTS, 0)
        purchased = dict.fromkeys(INGREDIENTS, 0)
        purchases_cost = 0
        if not bankrupt:
            # updating discarded based on the temporary stock update
            discarded = temp_stock.discarded(remaining) 
            remaining = {k: remaining[k] - discarded[k] for k in INGREDIENTS}
            if any(remaining[k] + purchases[k] > INGREDIENTS[k].capacity for k in INGREDIENTS):
                raise ValueError("purchase exceeds capacity")
            purchases_cost = sum(INGREDIENTS[k].price * purchases[k] for k in INGREDIENTS)
            if purchases_cost > cash_after_charges:
                raise ValueError("purchase is unaffordable")
            purchased = purchases
            remaining = {k: remaining[k] + purchased[k] for k in INGREDIENTS}

        # commit changes only after all rejection checks have passed
        temp_stock.update(remaining)
        self.stock = temp_stock

        for order in self.order_book.due_orders(self.week):
            if order.id in missed_order_ids:
                order.missed()
            elif order.id in fulfilled_order_ids:
                order.fulfilled()    
 
        opening_cash = self._cash
        self._cash = cash_after_charges - purchases_cost
        self.bankrupt = bankrupt
        record = {
            "week": self.week, "opening_cash": opening_cash, "closing_cash": self._cash,
            "workforce": workforce, "order_revenue": order_revenue,
            "walk_in_revenue": walk_in_revenue, "revenue": revenue, "wages": wages,
            "rent": rent, "purchases_cost": purchases_cost, "sales": sales,
            "opening_stock": opening_stock, "consumed": consumed, "discarded": discarded,
            "purchased": purchased, "closing_stock": dict(self.stock.quantities),
            "minutes_used": minutes, "bankrupt": bankrupt,
            "fulfilled_order_ids": fulfilled_order_ids, "missed_order_ids": missed_order_ids
        }
        self._history.append(record)
        self.week += 1
        return deepcopy(record)
