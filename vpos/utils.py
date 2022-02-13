
def get_calculated_fees(amount: float,
        fee: tuple, name: str = None,
        return_as_dict: bool = True):
    """
    Calculates the fees for an amount.
    fees must be a tuple containing the following values in the following order:
    The percentage rate, minimum amount to be withdrawn, maximum amount and default plus amount. like:
    (13, 100, 100, 0) or
    (0.25, None, None, 0)
    """

    percent, min_amount, max_amount, plus = fee
    if percent:
        fee_amount = (amount * (percent / 100)) + plus
        if min_amount and fee_amount < min_amount:
            expense = min_amount
        elif max_amount and fee_amount > max_amount:
            expense = max_amount
        else:
            expense = fee_amount
        
        if return_as_dict:
            return {
                'name': name,
                'amount': amount,
                'net_amount': amount - expense,
                'expense': expense,
                'fee_amount': fee_amount,
                'applied_plus_amount': plus,
                'applied_fee': percent,
                'applied_min_amount': min_amount,
                'applied_max_amount': max_amount
            }
        return amount, amount - expense, expense, fee_amount
    return None
