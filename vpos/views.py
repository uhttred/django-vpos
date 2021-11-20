import json

from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from vpos.models import Transaction

@csrf_exempt
def watch_transaction_confirmation(request: HttpRequest, transaction_id: str) -> HttpResponse:
    """View to watch vPOS API Webhook with Transaction Confirmation"""
    if request.method == 'POST':
        # TODO: (security) check api signature (vPOS dependency)
        # ...
        transaction: Transaction = get_object_or_404(Transaction,
            id=transaction_id)
        data: dict = json.loads(request.body)
        if not transaction.payment and data.get('id') == transaction.key:
            if transaction.confirm(data):
                return HttpResponse(status=200)
            return HttpResponse(status=409)
        return HttpResponse(status=403)
    return HttpResponse(status=405)
