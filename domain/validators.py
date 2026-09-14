slug = "123456"

def is_valid_slug(slug: str):

    return len(slug) == 6 and slug.isalnum()