import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from vpos.validators import PhoneValidator
from vpos.api import VposAPI


class Manager(models.Manager):
    pass


class TransactionType(models.TextChoices):
    PAYMENT = 'payment', _('Payment')
    REFUND = 'refund', ('Refund')


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
        null=True,
        default=None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api = VposAPI(
            idempotency_key=self.idempotency_key)

    @property
    def is_paid(self) -> bool:
        """Paid Status"""
        pass
    
    @property
    def idempotency_key(self) -> str:
        return str(self.id)
    
    @property
    def location(self) -> str:
        """location string provided by vPOS api header"""
        return self.data.get('location', '')

    def request(self, polling: bool = False) -> bool:
        """Request Payment or Refund"""
        if not self.requested:
            if self.type == self.Type.REFUND:
                location = self.api.create(type='refund',
                    polling=polling,
                    parent_id=self.parent.id)
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
