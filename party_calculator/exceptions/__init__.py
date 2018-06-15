class PartyCalculatorException(Exception):
    """Base Party Calculator exception"""
    pass


class MemberAlreadyInParty(PartyCalculatorException):
    pass


class NoSuchPartyState(PartyCalculatorException):
    pass


class TemplatePartyScheduleIsNotSet(PartyCalculatorException):
    pass


class NoSuchTemplatePartyState(PartyCalculatorException):
    pass
