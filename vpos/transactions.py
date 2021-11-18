from typing import Union

from vpos.models import Transaction


def create(mobile: str, amount: Union[str, float], is_payment: bool = True) -> Transaction:
    """Creates new Payment or Refund Transaction"""
    type = Transaction.Type.PAYMENT if is_payment else Transaction.Type.REFUND
    transaction: Transaction = Transaction.objects.create(
        type=type,
        mobile=mobile,
        amount=amount)
    return transaction
    