class BrowserError(Exception):
    """Base browser error."""
    pass


class InvalidCookiePath(BrowserError):
    """Invalid Cookie path."""
    def __init__(self, cookies_path):
        self.cookies_path = cookies_path

    def __str__(self):
        return f'Invalid cookies path: {self.cookies_path}'


class BrowserSetupError(BrowserError):
    """Failed to load browser."""
    pass


class PageCreationError(BrowserError):
    """Failed to create a new page."""


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


class ParserError(Exception):
    """Base parser error."""
    pass


class SearchError(ParserError):
    """Search error. No posts found."""
pass


class ParsePostError(ParserError):
    """Post parsing error."""

    def __init__(self, link):
        self.link = link

    def __str__(self):
        return f'Post parsing error. Cannot parse {self.link}'


class SaveJsonError(Exception):
    """Failed to save JSON."""
    pass


class CookiesSaveError(Exception):
    """Failed to save cookies."""
    pass
