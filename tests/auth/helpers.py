def register(client, payload):
    return client.post("/api/v1/auth/register", json=payload)


def login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def me(client, token):
    return client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )