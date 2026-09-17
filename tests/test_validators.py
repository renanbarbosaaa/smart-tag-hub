import pytest
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