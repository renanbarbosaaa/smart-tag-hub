slug = "aX7b9Y1"

def is_valid_slug(slug: str):
    condicao_de_tamanho = len(slug)
    condicao_alfanumerica = slug.isalnum()

    if (condicao_de_tamanho == 6) and condicao_alfanumerica == True:
        return True
    else:
        return False
    