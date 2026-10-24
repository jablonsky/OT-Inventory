def test_public_demo_is_available_without_an_account(client):
    response = client.get("/demo")
    assert response.status_code == 200
    assert b"OT device inventory demo" in response.data
    assert b"plc-pack-01" in response.data
    assert b"fictional records" in response.data


def test_security_headers_are_added(client):
    response = client.get("/demo")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
