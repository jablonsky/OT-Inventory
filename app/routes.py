from types import SimpleNamespace

from flask import Blueprint, render_template, flash, redirect, url_for, abort # import flask elements / objects

from app.forms import DeviceForm, InitialAdminForm, LoginForm, LogoutForm, CreateUserForm
from app.models import Device, User # required model for the route to create a new device in db
from app.extensions import db # import db object
from app.decorators import roles_required

from flask_login import login_user, current_user, login_required, logout_user



# blueprint to import flask application directly 
main = Blueprint("main", __name__)

DEMO_DEVICES = (
    SimpleNamespace(
        hostname="plc-pack-01",
        ip_address="10.20.10.21",
        prefix_length=24,
        device_type="PLC",
        vendor="Siemens",
        model="SIMATIC S7-1500",
        site="North Plant",
        purdue_level="1",
        zone="Cell/Area Zone",
        status="active",
    ),
    SimpleNamespace(
        hostname="hmi-line-02",
        ip_address="10.20.20.42",
        prefix_length=24,
        device_type="HMI",
        vendor="Rockwell Automation",
        model="PanelView Plus 7",
        site="North Plant",
        purdue_level="2",
        zone="Supervisory Control Zone",
        status="maintenance",
    ),
    SimpleNamespace(
        hostname="hist-core-01",
        ip_address="10.20.30.15",
        prefix_length=24,
        device_type="Historian",
        vendor="AVEVA",
        model="Historian Server",
        site="Central Operations",
        purdue_level="3",
        zone="Site Operations Zone",
        status="active",
    ),
    SimpleNamespace(
        hostname="fw-otdmz-01",
        ip_address="172.20.35.1",
        prefix_length=24,
        device_type="Firewall",
        vendor="Fortinet",
        model="FortiGate 100F",
        site="Central Operations",
        purdue_level="3.5",
        zone="OT DMZ",
        status="active",
    ),
)

@main.app_context_processor
def inject_logout_form():
    if current_user.is_authenticated:
        return {"logout_form": LogoutForm()}
    
    return{}


@main.route("/demo")
def demo():
    return render_template("demo.html", devices=DEMO_DEVICES)



@main.route("/setup", methods=["GET", "POST"])
def setup():

    existing_user_id = db.session.scalar(db.select(User.id).limit(1))
    if existing_user_id is not None:
        abort(404)

    form = InitialAdminForm()

    if form.validate_on_submit():
        user = User(
            name = form.name.data.strip(),
            email = form.email.data.strip().lower(),
            role = "admin",
            active = True
        )
        user.set_password(form.password.data)

        # initiate the first user in the database
        db.session.add(user)
        db.session.commit()

        login_user(user)


        flash("Administrator account created successfully.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("setup.html", form=form)
    


@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = db.session.scalar(
            db.select(User).where(User.email == email)
        )

        if user is None or not user.check_password(form.password.data):
            # if user does not exist in db or password is not matching
            flash("Invalid email address or password.", "danger")
            return redirect(url_for("main.login"))

        if not user.is_active:
            flash("This account is disabled. Contact an administrator.", "warning")
            return redirect(url_for("main.login"))


        login_user(user, remember=form.remember_me.data)

        flash(f"Welcome back, {user.name}.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("login.html", form=form)


@main.route("/logout", methods=["POST"])
@login_required
def logout():
    form = LogoutForm()

    if not form.validate_on_submit():
        abort(400)

    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("main.login"))


@main.route("/admin/users")
@roles_required("admin")
def manage_users():
    users = db.session.scalars(
        db.select(User).order_by(User.active.desc(),User.name)
    ).all()

    active_user_count = sum(user.active for user in users)

    return render_template("manage_users.html", users=users, active_user_count=active_user_count)


@main.route("/admin/users/new", methods=["GET", "POST"]) 
@roles_required("admin")
def create_user():

    form = CreateUserForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        existing_user_id = db.session.scalar(
            db.select(User.id).where(User.email == email)
        )

        if existing_user_id is not None:
            form.email.errors.append("A user with this email address already exists.")
        else:
            user = User(
                name = form.name.data.strip(),
                email = email,
                role = form.role.data,
                active = True,
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash(f"Account created for {user.name}.", "success")
            return redirect(url_for("main.manage_users"))

    return render_template("create_user.html", form=form)



@main.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html") 


@main.route("/inventory")
@login_required
def inventory():

    devices = Device.query.all() # query model from database, excecute and return query in the py list

    return render_template("inventory.html", devices=devices) # for device left side Jinja, right side database query


@main.route("/devices/<int:device_id>")
@login_required
def device_details(device_id):
    device = db.session.get(Device, device_id)
    if device is None:
        abort(404)

    return render_template("device_details.html", device=device)


@main.route("/devices/add", methods=["GET", "POST"])
@roles_required("editor", "admin")
def add_device():

    form = DeviceForm()
    if form.validate_on_submit():
        existing_device_id = db.session.scalar(
            db.select(Device.id).where(Device.ip_address == form.ip_address.data)
        )

        if existing_device_id is not None:
            form.ip_address.errors.append("A device with this IP address already exists.")
        else:
            device = Device()
            _apply_device_form(device, form)
            db.session.add(device) # places devie into SQLAlchemy pending
            db.session.commit() # write pendiing pernamently to database
            flash("Device added successfully.", "success")
            return redirect(url_for("main.inventory"))
                

    return render_template(
        "add_device.html",
        form=form,
        page_title="Add Device",
        section_label="New inventory record",
        heading="Add OT device",
        introduction="Enter the information currently known about this asset.",
    )


@main.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
@roles_required("editor", "admin")
def edit_device(device_id):
    
    device = db.session.get(Device, device_id)
    if device is None:
        abort(404)

    form = DeviceForm(obj=device)
    form.submit.label.text = "Save changes"

    if form.validate_on_submit():
        existing_device_id = db.session.scalar(
            db.select(Device.id).where(
                Device.ip_address == form.ip_address.data,
                Device.id != device.id,
            )
        )

        if existing_device_id is not None:
            form.ip_address.errors.append("A device with this IP address already exists.")
        else:
            _apply_device_form(device, form)
            db.session.commit()
            flash(f"{device.hostname} updated successfully.", "success")
            return redirect(url_for("main.inventory"))

    return render_template(
        "add_device.html",
        form=form,
        page_title="Edit Device",
        section_label="Inventory maintenance",
        heading=f"Edit {device.hostname}",
        introduction="Update this asset's identity, classification and location.",
    )


def _apply_device_form(device, form):
    device.hostname = form.hostname.data.strip()
    device.ip_address = form.ip_address.data.strip()
    device.prefix_length = form.prefix_length.data
    device.device_type = form.device_type.data
    device.vendor = form.vendor.data.strip()
    device.model = form.model.data.strip() if form.model.data else None
    device.serial_number = form.serial_number.data.strip() if form.serial_number.data else None
    device.site = form.site.data.strip() if form.site.data else None
    device.location = form.location.data.strip() if form.location.data else None
    device.vlan = form.vlan.data.strip() if form.vlan.data else None
    device.purdue_level = form.purdue_level.data
    device.zone = form.zone.data
    device.status = form.status.data
    device.description = form.description.data.strip() if form.description.data else None
