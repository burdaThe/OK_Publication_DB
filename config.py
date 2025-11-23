from dataclasses import dataclass
from src.errors import InvalidPostsNumber, InvalidSearchTargetLength


@dataclass
class Config:
    """Core configuration of the OK-parser."""
    search_target: str
    n_posts: int = 5
    headless: bool = False
    timeout: int = 60000
    cookies_path: str = 'ok_cookies.json'
    output_path: str = 'output.json'

    def __post_init__(self):
        if self.n_posts < 1 or self.n_posts > 99999:
            raise InvalidPostsNumber(num=self.n_posts)

        if len(self.search_target) == 0:
            raise InvalidSearchTargetLength(length=len(self.search_target))

        if not self.search_target.strip():
            raise InvalidSearchTargetLength(length=0)

    @property
    def search_url(self) -> str:
        """Returns search url."""
        return f'https://ok.ru/dk?st.cmd=searchResult&st.mode=Content&st.query={self.search_target}'
