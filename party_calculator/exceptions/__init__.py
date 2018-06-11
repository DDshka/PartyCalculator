class PartyCalculatorException(Exception):
    """Base Party Calculator exception"""
    pass


class MemberAlreadyInParty(PartyCalculatorException):
    pass
