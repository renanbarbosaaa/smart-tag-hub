from domain.validators import is_valid_slug
from domain.validators import is_valid_url

def test_slug_validate_return_true():
    # perfect slug w/ 6 characters
    assert is_valid_slug("aX7b9Y") == True 
    assert is_valid_slug("123456") == True
    assert is_valid_slug("abcdef") == True

def test_slug_with_wrong_size_return_false():
    # limit testing (Boundary Testing)
    assert is_valid_slug("abcde") == False  # 5 char
    assert is_valid_slug("aX7b9Y1") == False # 7 char
    assert is_valid_slug("") == False       # Empty

def test_slug_with_invalid_characters_return_false():
    # injection test and special characters
    assert is_valid_slug("aX-b9Y") == False # hyphen
    assert is_valid_slug("aX7b 9") == False # space
    assert is_valid_slug("drop x") == False # SQL Injection
    assert is_valid_slug("aX7b9@") == False # symbol

def test_slug_with_non_ascii_characters_return_false():
    # str.isalnum() accepts unicode letters and digits, the slug must be base62 only
    assert is_valid_slug("ção123") == False # accented letters
    assert is_valid_slug("١٢٣٤٥٦") == False # arabic-indic digits

def test_url_valid_return_true():
    # perfect url with path directing for a api call that will reach the database
    assert is_valid_url("https://www.pathto.com.br/test1") == True # original domain w/ path
    assert is_valid_url("https://www.linkedin.com/in/renan") == True 
    assert is_valid_url("https://api.dominio.com/v1/users?id=1") == True # api call

def test_url_invalid_path_return_false():
    # url without a path that is still "valid", but not for api call aiming to get the real link
    assert is_valid_url("http://meusite.com.br") == False # url without path
    assert is_valid_url("www.google.com") == False  #

def test_url_malicious_return_false():
    # malicious paths that wanna get privacy data
    assert is_valid_url("javascript:alert(1)") == False
    assert is_valid_url("ftp://meuserver.com/arquivo.zip") == False

def test_url_over_max_length_return_false():
    # the database column holds up to 2048 characters
    base = "https://www.linkedin.com/"
    assert is_valid_url(base + "a" * (2048 - len(base))) == True   # exactly 2048
    assert is_valid_url(base + "a" * (2049 - len(base))) == False  # 2049

def test_url_malformed_does_not_raise_and_return_false():
    # urlparse raises ValueError on some malformed hosts, it must never reach the API as a 500
    assert is_valid_url("http://[::1/path") == False