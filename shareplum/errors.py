class ShareplumError(Exception):
    def __init__(self, msg, details=None):
        if details:
            super().__init__(f"{msg} : {details}")
        else:
            super().__init__(msg)


class ShareplumRequestError(ShareplumError):
    pass
