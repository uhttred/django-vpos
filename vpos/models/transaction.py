import uuid
from typing import Union

from django.db import models
from django.utils.translation import gettext_lazy as _

from vpos.configs import conf
from vpos.validators import PhoneValidator
from vpos.api import VposAPI


class TransactionType(models.TextChoices):
    PAYMENT = 'payment', _('Payment')
    REFUND = 'refund', ('Refund')


class Manager(models.Manager):
    
    def create_refund(self, parent):
        """Creates a new Refund Transaction"""
        transaction = self.model(
            parent=parent,
            type=TransactionType.REFUND,
            mobile=parent.mobile,
            amount=parent.amount)
        if conf.MODE == 'production':
            transaction.full_clean()
        transaction.save()
        return transaction
    
    def create_payment(self, mobile: str, amount: str):
        """Creates a new Refund Transaction"""
        transaction = self.model(
            type=TransactionType.PAYMENT,
            mobile=mobile,
            amount=amount,
            parent=None)
        if conf.MODE == 'production':
            transaction.full_clean()
        transaction.save()
        return transaction


class Transaction(models.Model):

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transaction')
    
    Type = TransactionType
    objects = Manager()
    api: VposAPI

    id = models.UUIDField(_('id'),
        primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(_('location id'),
        max_length=25, null=True, default=None, editable=False)
    amount = models.DecimalField(_('amount'),
        max_digits=12, decimal_places=2, editable=False)
    mobile = models.CharField(_('mobile number'),
        max_length=15, validators=[PhoneValidator()], editable=False)
    type = models.CharField(_('type'),
        max_length=7, choices=Type.choices, editable=False)
    requested = models.BooleanField(_('was requested'), default=False, editable=False)
    data = models.JSONField(_('vpos transaction data'), default=dict, editable=False)
    parent = models.OneToOneField(
        'self',
        on_delete=models.CASCADE,
        verbose_name=(_('parent transaction')),
        related_name='refund',
        blank=True,
        null=True,
        default=None)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = VposAPI(
            idempotency_key=self.idempotency_key)

    @property
    def payment(self) -> Union[dict, None]:
        """Transaction Data from vPOS"""
        return self.data.get('transaction')
    
    @property
    def idempotency_key(self) -> str:
        return str(self.id)
    
    @property
    def location(self) -> str:
        """location string provided by vPOS api header"""
        return self.data.get('location', '')
    
    def check_payment(self, wait: bool = False) -> Union[dict, None]:
        """
        Check transaction status from vPOS API,
        return transaction data if transaction accepted/rejected
        else (if waiting) returns None
        """
        if not self.payment:
            if (transaction := self.api.check(self.key, wait=wait)):
                self.data.update({
                    'transaction': transaction})
                self.save()
                return transaction
            return None
        return self.payment

    def request(self, polling: bool = False) -> bool:
        """Request Payment or Refund"""
        if not self.requested:
            if self.type == self.Type.REFUND:
                location = self.api.create(type='refund',
                    polling=polling,
                    parent_id=self.parent.key)
            else:
                location = self.api.create(type='payment',
                    mobile=PhoneValidator.clean_number(self.mobile),
                    amount=str(self.amount),
                    polling=polling)
            assert location is not None
            self.__set_key(location)
            return True
        return False
    
    def __set_key(self, location: str) -> None:
        if not self.key:
            self.key = location.split('/')[-1]
            self.data.update({'location': location})
            self.save()
