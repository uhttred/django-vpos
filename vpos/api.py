import time
import requests

from typing import Union
from requests import Response
from vpos.configs import conf


class VposAPI:

    """
    Vpos API Interaction
    Class for vpos.models.Transaction
    """

    __idempotency_key: str

    def __init__(self, idempotency_key: str) -> None:
        self.__idempotency_key = idempotency_key
    
    def create(self, **kwargs) -> Union[None, str]:
        """
        Create new Payment or Refund
        Expect this named args
            - type (str)
            - mobile (str|None)
            - amount (str|None)
            - parent_id (str|None)
            - polling: (bool)
        Returns location string
        """
        r = self.post('/transactions',
            data=self.__get_data_for_new_transaction(**kwargs))
        if r.status_code == 202:
            return r.headers.get('location')
        return None

    def check(self, request_id: str, wait: bool = False) -> Union[dict, None]:
        """
        Check Transaction Queued/Running Status
        Returns True if already completd else retuns False
        f payment process is running (waiting user answer, in queue or else)
        Will get the eta and wait (if True) some time to try the request again.
        When finished, will return the transaction data (by following the location header)
        """
        
        r = self.get(f'/requests/{request_id}')

        if r.status_code == 200:
            data: dict = r.json()
            if (eta := data.get('eta')) and wait:
                try:
                    seconds = int(float(eta)) + 1
                    time.sleep(seconds if seconds <= 90 else 90)
                except:
                    return None
                return self.check(request_id=request_id, wait=False)
            elif eta is None:
                return data # transaction data       
        return None

    # ---------------------------------------------------------------------
    # Base API Calls With Headers Configured

    def get(self, path: str, **kwargs) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.get(url, headers=self.__headers, **kwargs) as r:
            return r
        
    def post(self, path: str, data: dict = {}, **kwargs) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.post(url, json=data,
                headers=self.__headers, **kwargs) as r:
            return r
    
    def put(self, path: str, data: dict = {}, **kwargs) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.put(url, json=data,
                headers=self.__headers, **kwargs) as r:
            return r
    
    def delete(self, path: str, data: dict = {}, **kwargs) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.delete(url, json=data,
                headers=self.__headers, **kwargs) as r:
            return r

    @property
    def __headers(self) -> dict:
        headers = {
            'Content-Type': 'application/json',
            'Idempotency-Key': self.__idempotency_key,
            'Authorization': f'Bearer {conf.TOKEN}'}
        return headers
    
    @property
    def base_url(self) -> str:
        return conf.VPOS_BASE_URL
    
    @property
    def callback_url(self) -> str:
        return f'{conf.URL}/{self.__idempotency_key}'
    
    @property
    def vpos_id(self) -> str:
        return conf.VPOS_ID
    
    def __get_data_for_new_transaction(self, **kwargs) -> dict:
        """
        Expect this named args
            - type (str)
            - mobile (str|None)
            - amount (str|None)
            - parent_id (str|None)
            - polling: (bool)
        """
        if kwargs['type'] == 'refund':
            data = {
                'type': 'refund',
                'parent_transaction_id': kwargs.get('parent_id'),
                'supervisor_card': conf.get_supervisor_card()}
        else:
            data = {
                'type': 'payment',
                'pos_id': conf.POS_ID,
                'mobile': kwargs.get('mobile'),
                'amount': kwargs.get('amount')}

        if not kwargs.get('polling'):
            data['callback_url'] = self.callback_url
        return data
