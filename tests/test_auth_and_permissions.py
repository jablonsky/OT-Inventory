from app.extensions import db
from app.models import User


def test_first_user_can_complete_setup(client, app):
    response = client.post(
        "/setup",
        data={
            "name": "Initial Administrator",
            "email": "admin@example.com",
            "password": "a-secure-admin-password",
            "confirm_password": "a-secure-admin-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Administrator account created successfully" in response.data
    with app.app_context():
        user = db.session.scalar(db.select(User))
        assert user.email == "admin@example.com"
        assert user.role == "admin"


def test_setup_is_hidden_after_a_user_exists(client, create_user):
    create_user("existing@example.com", role="admin")
    assert client.get("/setup").status_code == 404


def test_login_and_logout(client, create_user, login):
    create_user("viewer@example.com")

    response = login("viewer@example.com")
    assert b"Welcome back" in response.data

    response = client.post("/logout", follow_redirects=True)
    assert b"You have been signed out" in response.data


def test_disabled_user_cannot_sign_in(client, create_user, login):
    create_user("disabled@example.com", active=False)
    response = login("disabled@example.com")
    assert b"This account is disabled" in response.data


def test_viewer_cannot_add_devices(client, create_user, login):
    create_user("viewer@example.com", role="viewer")
    login("viewer@example.com")
    assert client.get("/devices/add").status_code == 403


def test_editor_can_add_but_cannot_manage_users(client, create_user, login):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")
    assert client.get("/devices/add").status_code == 200
    assert client.get("/admin/users").status_code == 403


def test_admin_can_manage_users(client, create_user, login):
    create_user("admin@example.com", role="admin")
    login("admin@example.com")
    assert client.get("/admin/users").status_code == 200
