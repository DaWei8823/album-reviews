from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as dt
from dataclasses import dataclass
import multiprocessing as mp

@dataclass
class AlbumReview:
    url:str
    author:str
    author_url:str
    author_url:str
    title:str
    pub_date:dt.datetime
    artist:str
    artist_url:str
    cover_art_url:str
    rating:float
    genre:str
    review_abstract:str
    review_text:str


def get_html(url:str) -> str:
    with urlopen(url) as resp:
        return resp.read()

def get_review_urls(from_date:dt.datetime) -> [str]:

    page_number = 1
    urls = []

    while(True):
        html = get_html(f"https://pitchfork.com/reviews/albums/?page={page_number}")
        review_divs = BeautifulSoup(html, "html.parser").find_all('div', {"class": "review"})

        for div in review_divs:
            date, url = parse_date_and_url(div)
            if(date<from_date):
                return urls
            urls.append(url)

        page_number += 1


def parse_date_and_url(review_div:str) -> (dt.datetime,str):
    return (dt.datetime.strptime(review_div.time['datetime'],"%Y-%m-%dT%H:%M:%S"), review_div.a['href'])

def parse_album_review(html:str) -> AlbumReview:
    soup = BeautifulSoup(html, "html.parser")

    author_detail_a = soup.find("div", { "class" : "article-meta article-meta--reviews"}).find("ul", {"class": "authors-detail"}).a

    tombstone_heading = soup.find("hgroup", { "class": "single-album-tombstone__headings"})

    artist_a = tombstone_heading.a

    review_body = soup.find("div", {"class": "row review-body"})
    review_genre = review_body.find("a", {"class": "genre-list__link"})
    return AlbumReview(
        url = soup.find("link", {"rel" : "canonical"})["href"],
        author = author_detail_a.text,
        author_url = get_full_pitchfork_url(author_detail_a["href"]),
        title = tombstone_heading.find("h1",{"class": "single-album-tombstone__review-title"}).text,
        pub_date = dt.datetime.strptime(soup.time["datetime"],"%Y-%m-%dT%H:%M:%S"),
        artist = artist_a.text,
        artist_url = get_full_pitchfork_url(artist_a["href"]),
        cover_art_url = soup.find("div", {"class" : "single-album-tombstone__art" }).img["src"],
        rating = float(soup.find("div", {"class": "review-detail"}).find("div", "score-circle").text),
        genre= review_genre.text if review_genre is not None else None,
        review_abstract= review_body.find("div", {"class": "review-detail__abstract"}).text,
        review_text= review_body.find("div", {"class": "review-detail__text clearfix"}).text)

def get_full_pitchfork_url(relative_url:str) -> str:
    return base_url + relative_url

def get_album_review_from_relative_url(relative_url:str) -> AlbumReview:
    html = get_html(get_full_pitchfork_url(relative_url))
    
    try:
        return parse_album_review(html)
    except AttributeError as e:
        print(f"FAILURE: {relative_url}")
        print(e)

def get_album_review_from_artist_and_album(artist:str, album:str) -> AlbumReview:
    relative_url = get_relative_url_for_review(artist,album)
    return get_album_review_from_relative_url(relative_url)

def get_relative_url_for_review(artist:str, album:str) -> str:
    album_tag = album.replace(" ", "-")
    artist_tag = artist.replace(" ", "-")
    return "/reviews/albums/" + artist_tag.lower() + "-" + album_tag.lower()


def print_review(review):
    print("-------------------------------------------------------------")
    print(f"Title: {review.title}")
    print(f"Pub Date: {review.pub_date}")
    print(f"Author: {review.author}")
    print(f"Author Url: {review.author_url}")
    print(f"Review Url: {review.url}")
    print(f"Artist: {review.artist}")
    print(f"Artist Url: {review.artist_url}")
    print(f"Rating: {review.rating}")
    print(f"Review Abstract: {review.review_abstract}")
    print(f"Review Text: {review.review_text[:100]}")



base_url = "https://pitchfork.com"

if __name__ == '__main__':

    review = get_album_review_from_relative_url('/reviews/albums/yaeji-what-we-drew/')

    with open('album-review.txt', 'w', encoding = "utf-8") as f:
        f.write(review.review_text)

    # urls = get_review_urls(dt.datetime(2020, 3, 30))

    # pool = mp.Pool(int(mp.cpu_count()*0.67))
    # reviews = pool.map(get_album_review_from_relative_url, urls)

    # for review in reviews:    
    #     print_review(review)

