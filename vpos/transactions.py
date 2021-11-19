from vpos.models import Transaction


def create(mobile: str,
        amount: str,
        parent: Transaction = None) -> Transaction:
    """
    Creates new Payment or Refund Transaction
    If parent is set creates a Refund Transaction
    """
    if not parent:
        return Transaction.objects.create_payment(
            mobile=mobile, amount=amount)
    return Transaction.objects.create_refund(
        parent=parent)
    