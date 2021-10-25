from asyncio import TimeoutError


class MDCError(Exception):
    pass


class MDCTLSRequired(Exception):
    pass


class MDCTLSAuthFailed(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)

    def __str__(self):
        if self.code == 1:
            return 'Wrong pin'
        elif self.code == 2:
            return 'Blocked'
        else:
            return f'Unknown code: {self.code}'


class MDCTimeoutError(MDCError, TimeoutError):
    pass


class MDCReadTimeoutError(MDCTimeoutError):
    pass


class MDCResponseError(MDCError):
    pass


class NAKError(MDCError):
    def __init__(self, error_code):
        self.error_code = error_code
        super().__init__(error_code)

    def __str__(self):
        return f'Negative Acknowledgement [error_code {self.error_code}]'
