import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneAOValidator(validators.RegexValidator):
    
    regex = r'^(?:(\+244|00244))?(9)(1|2|3|4|9)([\d]{7,7})$'
    default_replace = r'\2\3\4'
    message =  _('Invalid national phone number of angola')

    @classmethod
    def match(cls, string):
        return re.match(cls.regex, string)
    
    @classmethod
    def clean_number(cls, phone: str):
        return re.sub(cls.regex, cls.default_replace, phone)


# default
PhoneValidator = PhoneAOValidator
