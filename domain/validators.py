from urllib.parse import urlparse

slug = "123456"


def is_valid_slug(slug: str):

    return len(slug) == 6 and slug.isalnum()

url = "https://www.pathto.com.br"

scheme = {"http", "https"}

def is_valid_url(url: str):
    parsed_url = urlparse(url)

    return (
        parsed_url.scheme in scheme and bool(parsed_url.netloc) 
        )
    