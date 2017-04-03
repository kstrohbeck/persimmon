class Result:
    def __init__(self, consumed, expected):
        self.consumed = consumed
        self.expected = expected


class Success(Result):
    def __init__(self, values, consumed=False, expected=None):
        super().__init__(consumed, expected or [])
        self.values = values


class Failure(Result):
    def __init__(self, unexpected, consumed=False, expected=None):
        super().__init__(consumed, expected or [])
        self.unexpected = unexpected
