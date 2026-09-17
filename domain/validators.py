from urllib.parse import urlparse

def is_valid_slug(slug: str):

    return len(slug) == 6 and slug.isalnum()

scheme = {"http", "https"}

def is_valid_url(url: str):
    
    parsed_url = urlparse(url)

    return (
        parsed_url.scheme in scheme and bool(parsed_url.netloc) and bool(parsed_url.path) 
        )
    