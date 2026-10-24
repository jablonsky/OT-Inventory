import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test-inventory.db"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret-key",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "WTF_CSRF_ENABLED": False,
            "SESSION_COOKIE_SECURE": False,
            "REMEMBER_COOKIE_SECURE": False,
        }
    )

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def create_user(app):
    def _create_user(email, role="viewer", password="a-strong-test-password", active=True):
        with app.app_context():
            user = User(
                name=role.title(),
                email=email,
                role=role,
                active=active,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user.id

    return _create_user


@pytest.fixture()
def login(client):
    def _login(email, password="a-strong-test-password"):
        return client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    return _login


@pytest.fixture()
def device_form_data():
    def _device_form_data(**overrides):
        data = {
            "hostname": "plc-test-01",
            "ip_address": "10.0.0.10",
            "prefix_length": "24",
            "device_type": "PLC",
            "vendor": "Test Vendor",
            "model": "Test Model",
            "serial_number": "SERIAL-001",
            "site": "Test Site",
            "location": "Line 1",
            "vlan": "100",
            "purdue_level": "1",
            "zone": "Cell/Area Zone",
            "status": "active",
            "description": "Fictional test asset",
        }
        data.update(overrides)
        return data

    return _device_form_data
