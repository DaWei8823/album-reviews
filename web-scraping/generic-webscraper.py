from bs4 import BeautifulSoup
from urllib.request import urlopen


def get_html(url:str) -> str:
    with urlopen(url) as resp:
        return resp.read()

def get_review_text(html:str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    soup.children