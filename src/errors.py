class BrowserError(Exception):
    """Base browser error."""
    pass


class ConfigError(Exception):
    """Base confid error."""
    pass


class InvalidPostsNumber(ConfigError):
    """Invalid posts number. Expected > 0 and < 100000."""
    def __init__(self, num):
        self.num = num

    def __str__(self):
        return f'Invalid posts number. Expected > 0 and < 100000. Got {self.num}.'


class InvalidSearchTargetLength(ConfigError):
    """Invalid search target length. Expected > 0."""
    def __init__(self, length):
        self.length = length

    def __str__(self):
        return f'Invalid search target length. Got {self.length}. Expected > 0.'
