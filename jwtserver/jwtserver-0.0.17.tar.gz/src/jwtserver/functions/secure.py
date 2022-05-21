from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt", "ldap_salted_md5"],
                           sha256_crypt__default_rounds=649342,
                           ldap_salted_md5__salt_size=16)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
