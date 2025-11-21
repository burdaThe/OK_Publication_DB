from dataclasses import dataclass


@dataclass
class Config:
    """Core configuration of the OK-parser."""
    search_target: str
    n_posts: int = 5
    headless: bool = True
    timeout: int = 60000
    cookies_path: str = "ok_cookies.json"
    output_path: str = "output.json"

    @property
    def search_url(self) -> str:
        """Returns search url."""
        return f"https://ok.ru/dk?st.cmd=searchResult&st.mode=Content&st.query={self.search_target}"
