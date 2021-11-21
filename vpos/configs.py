from django.conf import settings
from django.utils.translation import gettext_lazy as _

from vpos.exceptions import VposConfigurationError as Err


DEFAULTS: dict = {
    # required
    'POS_ID': None,
    'TOKEN': None,
    'URL': None,
    'MODE': 'production',
    'VPOS_SUPERVISOR_CARD': None,
    'VPOS_BASE_URL': 'https://vpos.ao/api/v1',
    # optionals
    'VPOS_TEST_SUPERVISOR_CARD': '9610123456123412341234123456789012345'}


VPOS_STATUS_REASON: dict = {
    # client
    '3000': _('Refused by client'),
    # Processor
    '2010': _('Request was refused by the processor'),
    '2009': _('Parent transaction is too old to be refunded'),
    '2008': _('Invalid merchant email'),
    '2007': _('Invalid or Inactive supervisor card'),
    '2006': _('Insufficient funds in POS available for refund'),
    '2005': _('POS is closed and unable to accept transactions'),
    '2004': _('Request timed-out and was refused by the processor'),
    '2003': _('Card or network daily limit exceeded'),
    '2002': _('Refused by the card issuer'),
    '2001': _("Insufficient funds in client's account"),
    '2000': _('Generic processor error'),
    # Gateway
    '1003': _('Parent transaction ID of refund request is not an accepted Payment'),
    '1002': _('Gateway is not authorized to execute transactions on the specified POS'),
    '1001': _('Request timed-out and will not be processed'),
    '1000': _('Generic gateway error')}


class VposSettings:

    __defaults: dict

    def __init__(self, defaults: dict = None, user_settings: dict = None) -> None:
        if user_settings:
            self.__settings = user_settings
        self.__defaults = defaults or DEFAULTS

    @property
    def settigs(self) -> dict:
        if not hasattr(self, '__settings'):
            return getattr(settings, 'VPOS', {})
        return self.__settings
    
    def validate(self):
        """configurations validation"""
        for attr in dir(self):
            if 'validate_' in attr:
                getattr(self, attr)()
    
    def validate_mode(self):
        modes = ('production', 'sandbox')
        if self.MODE not in modes:
            raise Err(
                "Invalid MODE: '%s'. Must be " 
                "production or sandbox" % self.MODE)
    
    def validate_token(self):
        if not self.POS_ID:
            raise Err('TOKEN is required')
    
    def validate_url(self):
        if not self.POS_ID:
            raise Err('URL is required for callback transaction confirmation')
    
    def validate_vpos_base_url(self):
        if not self.POS_ID:
            raise Err('VPOS_BASE_URL is required')
    
    def validate_vpos_supervisor_card(self):
        if not self.POS_ID:
            raise Err('VPOS_SUPERVISOR_CARD is required')
    
    def validate_pos_id(self):
        if not self.POS_ID:
            raise Err('POS_ID is required')

    def get_supervisor_card(self) -> str:
        if self.MODE == 'sandbox':
            return self.VPOS_TEST_SUPERVISOR_CARD
        return self.VPOS_SUPERVISOR_CARD

    def __getattr__(self, attr: str):
        if attr not in self.__defaults:
            raise AttributeError("Invalid VPOS setting: '%s'" % attr)
        try:
            value = self.settigs[attr]
        except KeyError:
            value = self.__defaults[attr]
        setattr(self, attr, value)
        return value
    

conf = VposSettings()
