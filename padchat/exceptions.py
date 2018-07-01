class PadchatException(Exception):
    pass


class UnknowLoginType(PadchatException):
    pass


class InvalidateValueError(PadchatException):
    pass


class InstanceNotInit(PadchatException):
    pass

