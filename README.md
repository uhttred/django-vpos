# Django vPOS

Django vPOS is a [Django Framework](https://www.djangoproject.com/) application/library that facilitates the integration of your Django project with the [vPOS](https://vpos.ao) API Payment Gateway.

----------------------------------------------------------------------------------

## Some Features

The Django vPOS really comes to facilitate the integration to the vPOS API, leaving all interaction with vPOS totally out of the box. Letting you focus more on data validation and/or your business logic.

* Verify payment directly from a transaction instance
* Recognize confirmed transaction automatically using vPOS callback url
* Signals, to get dynamically confirmed transactions instances

----------------------------------------------------------------------------------

## Installation

Simple **django-vpos** can be installed with ``pip``:

    pip install django-vpos

Or from this repository:

    pip install -e git+https://github.com/txiocoder/django-vpos.git@main#egg=vpos

These are the officially supported python and package versions. Other versions will probably work

## Configuration

As stated above, Django vPOS is a django Application. To configure on your project you simply need to add ``vpos`` to your ``INSTALLED_APPS`` and configure the ``VPOS`` variable in the ``settings.py`` file. More details about how to configure the ``VPOS`` variable below.

```python
INSTALLED_APPS: list = [
    'vpos',
]

VPOS: dict = {
    'TOKEN': 'your-vpos-token',
    'POS_ID': 1234,
    # the base callback url without slash at end
    'URL': 'https://youproject.com/path/to/confirm',
    'MODE': 'production'}
```

Then, add ``vpos.urls ``to your URL configuration to route and handle all transaction confirmation coming from vPOS API callback.

In your ``project.urls``:

```python
from django.urls import path, include

urlpatterns: list = [
    path('path/to/confirm/', include('vpos.urls'))
]
```

Here the details about all attributes accpeted in ``VPOS``

| Attribute                 | Type    | Required  | Description                                                        |
|---------------------------|---------|-----------|--------------------------------------------------------------------|
| TOKEN                     | ``str`` | ``True``  | vPOS API Authorization Token                                       |
| POS_ID                    | ``int`` | ``True``  | The Point of Sale ID provided by EMIS                              |
| URL                       | ``str`` | ``True``  | Base Callback URL to handle transaction confirmation from vPOS API |
| MODE                      | ``str`` | ``False`` | The vPOS environment: ``production`` (default) or ``sandbox``      |
| VPOS_SUPERVISOR_CARD      | ``srt`` | ``True``  | The Supervisor card ID provided by EMIS                            |
| VPOS_BASE_URL             | ``str`` | ``False`` | vPOS API base URL. ``https://vpos.ao/api/v1`` (default)            |
| VPOS_TEST_SUPERVISOR_CARD | ``str`` | ``False`` | The Supervisor card for test, provided by vPOS                     |

----------------------------------------------------------------------------------

## Working with Transactions

Use the  ``vpos.references.create`` method to create new payment or refund transactions. This method will return an instance of ``vpos.models.Transaction``, which you can use to request payment/refund, check payment confirmation, get transaction data from **vPOS API** and more.

```python
from vpos.transactions import (
    Transaction,
    create)

# first, create payment transaction instance
t1: Transaction = create(
    mobile='900000000',
    amount='34500.45')
# then, request the payment
t1.request()
```

To create refund transaction, only specify the payment transaction to be refunded in create method. As shown below. Parent transaction must be an accepted payment transaction instance

```python
from vpos.transactions import (
    Transaction,
    create)

# first, get the payment transaction
t1: Transaction = Transaction.objects.get(
    id='transanction-id')
# second, create refund transaction instance
t2: Transaction = create(parent=t1)
# then, request the refund
t2.request()
```

If you prefer to use polling communication to manually check the transaction confirmation, instead of callback url. Just set ``polling=True`` as ``transaction.request`` argument

```python
t1: Transaction = create(
    mobile='900000000',
    amount='34500.45')

t1.request(polling=True)

# then, check the payment
t1.check_payment()

# You can also wait some time until the confirmation.
# This will wait at maximum 90 seconds. But first it will try to use the estimate time provided by vpos ETA.
# see: https://developer.vpos.ao/?shell#requests
t1.check_payment(wait=True)  
```

## Callback URL (Watch Payments)


To dynamically receive transaction confirmations from vPOS API, you only need to setup the ``URL`` key in ``VPOS`` variable configured in your ``settings.py``.

```python
VPOS: dict = {
    # other configurations...
    # the base callback url without slash at end
    'URL': 'https://youproject.com/path/to/confirm'}
```

Django vPOS will automaticaly recognize the related transaction and update the transaction data. To dynamiacly catch confirmed transactions see the session below about signals. And enjoy real-time payments update. 

## Signals, Getting Dynamically Confirmed Transactions

Signals are the best way to keep an eye on transactions confirmations. Let's imagine the following simple scenario. Activating a service after confirming payments.

First, the user need to request the service and payment. In your views you could do something like below:

```python
from service.modes import Service
from vpos.transactions import (
    Transaction,
    create)

def add_service(request) -> Response:
    # after validation and some business logic...
    # prepare the transaction
    t: Transaction = create(
        mobile=request.user.mobile,
        amount='1500')
    # create the service and add related transaction
    service: Service = Service.objects.create(
        owner=request.user,
        is_active=False,
        payment=t)
    # request user to pay
    t.request()
    return Response(status=201)
```

Yeah, I know... but just keep it simple. Then, we can use signals to activate the service when the user pay the requested payment transaction. Django vPOS has the ``vpos.signals.transaction_completed`` signal witch we can use to receive confirmed or completed transactions.

```python
from django.dispatch import receiver

from service.modes import Service

from vpos.models import Transaction
from vpos.signals import transaction_completed


@receiver(transaction_completed)
def active_service(sender, transaction: Transaction, **kwargs):
    if (transaction.accepted and transaction.is_payment):
        if hasattr(transaction, 'service'):
            service: Service = transaction.service
            service.is_active = True
            service.save()
            # publish the event...
```

That's it, I hope this module can be useful for you. Feel free to contribute and help me improve this module.