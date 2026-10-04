import hashlib

def fake_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()