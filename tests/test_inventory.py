from app.extensions import db
from app.models import Device


def test_prefix_zero_is_accepted(
    client, app, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    response = client.post(
        "/devices/add",
        data=device_form_data(prefix_length="0"),
        follow_redirects=True,
    )

    assert b"Device added successfully" in response.data
    with app.app_context():
        device = db.session.scalar(db.select(Device))
        assert device.prefix_length == 0


def test_duplicate_ip_address_is_rejected(
    client, app, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")
    client.post("/devices/add", data=device_form_data())

    response = client.post(
        "/devices/add",
        data=device_form_data(hostname="plc-test-02"),
    )

    assert b"A device with this IP address already exists" in response.data
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count(Device.id))) == 1
