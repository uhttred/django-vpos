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
        """
        data: dict = self.__get_data_for_new_transaction(**kwargs)
        r = self.post('/transactions', data=data)
        if r.status_code == 202:
            return r.headers.get('location')
        return None
    
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
                'supervisor_card': conf.supervisor_card}
        else:
            data = {
                'type': 'payment',
                'pos_id': conf.POS_ID,
                'mobile': kwargs.get('mobile'),
                'amount': kwargs.get('amount')}

        if not kwargs.get('polling'):
            data['callback_url'] = self.callback_url
        return data        
        
    # ---------------------------------------------------------------------
    # Base API Calls With Headers Configured

    def get(self, path: str, params: dict = {}) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.get(url, params=params, headers=self.headers) as r:
            return r
    
    def post(self, path: str, data: dict = {}, params: dict = {}) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.post(url, json=data,
                params=params, headers=self.headers) as r:
            return r
    
    def put(self, path: str, data: dict = {}, params: dict = {}) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.put(url, json=data,
                params=params, headers=self.headers) as r:
            return r
    
    def delete(self, path: str, data: dict = {}, params: dict = {}) -> Response:
        url: str = f'{self.base_url}{path}'
        with requests.delete(url, json=data,
                params=params, headers=self.headers) as r:
            return r

    @property
    def headers(self) -> dict:
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
