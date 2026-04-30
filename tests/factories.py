import uuid 


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def make_user_payload(
    *,
    name="Test User",
    email=None,
    password="12345678",
):
    return {
        "name": name,
        "email": email or unique_email(),
        "password": password,
    }