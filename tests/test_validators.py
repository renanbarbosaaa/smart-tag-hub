import pytest
from domain.validators import is_valid_slug
from domain.validators import is_valid_url

def test_slug_valido_retorna_true():
    # Um slug perfeitamente válido (6 caracteres alfanuméricos)
    assert is_valid_slug("aX7b9Y") == True
    assert is_valid_slug("123456") == True
    assert is_valid_slug("abcdef") == True

def test_slug_com_tamanho_invalido_retorna_false():
    # Testando limites (Boundary Testing)
    assert is_valid_slug("abcde") == False  # 5 caracteres
    assert is_valid_slug("aX7b9Y1") == False # 7 caracteres
    assert is_valid_slug("") == False       # Vazio

def test_slug_com_caracteres_invalidos_retorna_false():
    # Testando injeções e caracteres especiais
    assert is_valid_slug("aX-b9Y") == False # Hífen
    assert is_valid_slug("aX7b 9") == False # Espaço
    assert is_valid_slug("drop x") == False # SQL Injection disfarçado
    assert is_valid_slug("aX7b9@") == False # Símbolo

def test_url_valida_com_http_ou_https_retorna_true():
    assert is_valid_url("https://www.linkedin.com/in/renan") == True
    assert is_valid_url("http://meusite.com.br") == True
    assert is_valid_url("https://api.dominio.com/v1/users?id=1") == True

def test_url_sem_protocolo_retorna_false():
    # O usuário esqueceu o http://
    assert is_valid_url("www.google.com") == False 

def test_url_com_protocolo_malicioso_retorna_false():
    # Tentativa de injeção de script ou acesso local
    assert is_valid_url("javascript:alert(1)") == False
    assert is_valid_url("ftp://meuserver.com/arquivo.zip") == False