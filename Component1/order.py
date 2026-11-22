'''orders in advance'''
from validation import integer
from product import PRODUCTS


class Order:
    """Check each order according to the frame and manage its status"""
    def __init__(self, id, product_id, quantity, collection_week):
        if not isinstance(id, str) or not id or id != id.strip():
            raise ValueError("Invalid order ID")
        if not isinstance(product_id, str) or product_id not in PRODUCTS:
            raise ValueError("Unknown product")
        self.id = id
        self.product_id = product_id
        self.quantity = integer(quantity, "quantity", 1)
        self.collection_week = integer(collection_week, "collection_week", 1, 12)
        self.status = "pending"

    def fulfilled(self):
        """update the status of fulfilled order"""
        self.status = "fulfilled"

    def missed(self):
        """update the status of missed order"""
        self.status = "missed"
