import csv
import io

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


def test_inventory_search_is_case_insensitive(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-siemens-01",
            vendor="Siemens",
            ip_address="10.0.0.10",
        ),
    )

    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-rockwell-01",
            vendor="Rockwell Automation",
            ip_address="10.0.0.11",
            serial_number="SERIAL-002",
        ),
    )

    response = client.get("/inventory?q=SIEMENS")

    assert response.status_code == 200
    assert b"plc-siemens-01" in response.data
    assert b"plc-rockwell-01" not in response.data


def test_inventory_can_be_filtered_by_status(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-active-01",
            ip_address="10.0.0.20",
            status="active",
        ),
    )

    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-maintenance-01",
            ip_address="10.0.0.21",
            serial_number="SERIAL-003",
            status="maintenance",
        ),
    )

    response = client.get("/inventory?status=maintenance")

    assert response.status_code == 200
    assert b"plc-maintenance-01" in response.data
    assert b"plc-active-01" not in response.data



def test_inventory_displays_filtered_empty_state(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post(
        "/devices/add",
        data=device_form_data(),
    )

    response = client.get("/inventory?q=device-that-does-not-exist")

    assert response.status_code == 200
    assert b"No devices match your filters" in response.data
    assert b"Clear filters" in response.data
    assert b"Add first device" not in response.data


def test_inventory_csv_export_is_a_download(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post("/devices/add", data=device_form_data())
    response = client.get("/inventory/export.csv")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert response.headers["Content-Disposition"].startswith(
        'attachment; filename="ot-inventory-'
    )
    assert response.headers["Content-Disposition"].endswith('.csv"')
    assert response.headers["Cache-Control"] == "no-store"

    rows = list(csv.reader(io.StringIO(response.data.decode("utf-8-sig"))))
    assert rows[0] == [
        "Hostname",
        "IP Address",
        "Prefix Length",
        "Device Type",
        "Vendor",
        "Model",
        "Serial Number",
        "Site",
        "Location",
        "VLAN",
        "Purdue Level",
        "Zone",
        "Device Status",
        "Device Description",
    ]
    assert rows[1][0] == "plc-test-01"
    assert rows[1][1] == "10.0.0.10"


def test_inventory_csv_export_uses_current_filters(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-active-01",
            ip_address="10.0.0.20",
            status="active",
        ),
    )
    client.post(
        "/devices/add",
        data=device_form_data(
            hostname="plc-maintenance-01",
            ip_address="10.0.0.21",
            serial_number="SERIAL-003",
            status="maintenance",
        ),
    )

    response = client.get("/inventory/export.csv?status=maintenance&q=PLC")
    rows = list(csv.reader(io.StringIO(response.data.decode("utf-8-sig"))))

    assert len(rows) == 2
    assert rows[1][0] == "plc-maintenance-01"


def test_inventory_csv_export_neutralizes_spreadsheet_formulas(
    client, create_user, login, device_form_data
):
    create_user("editor@example.com", role="editor")
    login("editor@example.com")

    client.post(
        "/devices/add",
        data=device_form_data(hostname="=DANGEROUS()"),
    )
    response = client.get("/inventory/export.csv")
    rows = list(csv.reader(io.StringIO(response.data.decode("utf-8-sig"))))

    assert rows[1][0] == "'=DANGEROUS()"
