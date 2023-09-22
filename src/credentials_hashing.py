from base64 import b64encode
from hashlib import sha256


def get_credentials_hash(username: str, password: str) -> str:
    digest = sha256((username + password).encode("utf8")).digest()
    return b64encode(digest, altchars=b"ab").decode("ascii").strip("=")
