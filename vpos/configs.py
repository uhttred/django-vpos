from django.conf import settings
from vpos.exceptions import VposConfigurationError as Err


DEFAULTS: dict = {
    'MODE': 'production',
    'TOKEN': '',
    'URL': '',
    'POS_ID': None,
    'VPOS_BASE_URL': 'https://vpos.ao/api/v1',
    'VPOS_SUPERVISOR_CARD': '',
    'VPOS_TEST_SUPERVISOR_CARD': '9610123456123412341234123456789012345'}


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
    
    def validate_pos_id(self):
        if not self.POS_ID:
            raise Err('POS_ID is required')

    def __getattr__(self, attr: str):
        if attr not in self.__defaults:
            raise AttributeError("Invalid VPOS setting: '%s'" % attr)
        try:
            value = self.settigs[attr]
        except KeyError:
            value = self.__defaults[attr]
        setattr(self, attr, value)
        return value
    
    @property
    def supervisor_card(self) -> str:
        if self.mode == 'sandbox':
            return self.VPOS_TEST_SUPERVISOR_CARD
        return self.VPOS_SUPERVISOR_CARD

conf = VposSettings()
