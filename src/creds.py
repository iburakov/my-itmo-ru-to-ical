from base64 import b64encode
from hashlib import sha256


def get_creds_hash(username: str, password: str) -> str:
    return b64encode(sha256((username + password).encode("utf8")).digest(), altchars=b"ab").decode("ascii").strip("=")
