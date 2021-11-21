from django.urls import path
from vpos.views import watch_transaction_confirmation


app_name = 'vpos'

urlpatterns: list = [
    path('<uuid:transaction_id>',
        watch_transaction_confirmation, name='confirmation'),
]
