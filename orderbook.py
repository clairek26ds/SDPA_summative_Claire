'''orders and status'''
from order import Order
from validation import integer

class OrderBook:
    def __init__(self, records, duration):   
        if not isinstance(records, list):
            raise ValueError("records need to be a list")
        duration = integer(duration, "duration", 1, 12)
        
        checked = set()
        validated_orders = []
        for record in records:
            if not isinstance(record, dict) or set(record) != {
                "id", "product_id", "quantity", "collection_week"}:
                raise ValueError("Invalid order record")
            order = Order(record["id"], record["product_id"], record["quantity"], record["collection_week"])
            if order.collection_week > duration:
                raise ValueError("collection week should be earlier than the duration")
            if order.id in checked:
                raise ValueError(f"found a duplicate order ID: {order.id}")
            checked.add(order.id)
            validated_orders.append(order)

        self.orders = validated_orders

    def due_orders(self, week):
        due_orders = [
            order for order in self.orders
            if order.collection_week == week
            and order.status == "pending"
        ]
        return sorted(due_orders, key = lambda order:order.id)
