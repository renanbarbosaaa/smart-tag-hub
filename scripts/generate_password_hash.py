from getpass import getpass

from api.security import hash_password


def main() -> None:
    password = getpass("Nova senha administrativa: ")
    confirmation = getpass("Confirme a senha: ")
    if password != confirmation:
        raise SystemExit("As senhas não coincidem.")
    if len(password) < 12:
        raise SystemExit("Use uma senha com pelo menos 12 caracteres.")
    print("\nADMIN_PASSWORD_HASH:")
    print(hash_password(password))


if __name__ == "__main__":
    main()
