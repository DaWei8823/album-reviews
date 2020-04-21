from bs4 import BeautifulSoup
import requests as req


def get_html(url:str) -> str:
    return req.get(url).content

def get_review_text(html:str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    soup.children