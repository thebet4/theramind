import bcrypt


def _truncate_password(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) <= 72:
        return password_bytes

    return password_bytes[:72]


def get_password_hash(password: str) -> str:
    password_bytes = _truncate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = _truncate_password(plain_password)
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)
