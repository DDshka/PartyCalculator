class PartyCalculatorException(Exception):
    """Base Party Calculator exception"""
    pass


class MemberAlreadyInPartyException(PartyCalculatorException):
    pass


class NoSuchPartyStateException(PartyCalculatorException):
    pass


class TemplatePartyScheduleIsNotSetException(PartyCalculatorException):
    pass


class NoSuchTemplatePartyStateException(PartyCalculatorException):
    pass


class TemplatePartyHasActiveRelatedPartyException(PartyCalculatorException):
    pass


class NegativeValueException(PartyCalculatorException):
    pass


class OAuthException(PartyCalculatorException):
    pass
