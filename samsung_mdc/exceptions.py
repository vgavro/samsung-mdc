from asyncio import TimeoutError


class MDCError(Exception):
    pass


class MDCTLSRequired(Exception):
    pass


class MDCTimeoutError(MDCError, TimeoutError):
    pass


class MDCResponseError(MDCError):
    pass


class NAKError(MDCError):
    def __init__(self, error_code):
        self.error_code = error_code
        super().__init__(error_code)

    def __str__(self):
        return f'Negative Acknowledgement [error_code {self.error_code}]'
