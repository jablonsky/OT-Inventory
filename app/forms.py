from flask_wtf import FlaskForm # base class Flask-WTF
from wtforms import SelectField, StringField, SubmitField, TextAreaField, IntegerField, PasswordField, BooleanField
from wtforms.validators import DataRequired, IPAddress, Length, Optional, NumberRange, Email, EqualTo

class DeviceForm(FlaskForm):

    hostname = StringField("Hostname", validators=[DataRequired(), Length(max=100)])
    ip_address = StringField("IP address", validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False), Length(max=45)])
    prefix_length = IntegerField("Subnet prefix length", validators=[DataRequired(), NumberRange(min=0, max=32)])    

    device_type = SelectField("Device Type", choices=[
        ("", "Select a device type"),
        ("PLC", "PLC"),
        ("HMI", "HMI"),
        ("SCADA Server", "SCADA server"),
        ("Historian", "Historian"),
        ("Network Switch", "Network switch"),
        ("Network Router", "Network router"),
        ("Firewall", "Firewall"),
        ("Engineering Workstation", "Enginnering workstation"),
        ("Other Server", "Other server"),
        ("Other", "Other")
    ], validators=[DataRequired()])
    vendor = StringField("Vendor", validators=[DataRequired(), Length(max=100)])
    model = StringField("Model", validators=[Optional(),Length(max=100)])
    serial_number = StringField("Serial Number", validators=[Optional(), Length(max=100)])
    site = StringField("Site", validators=[Optional(), Length(max=100)])
    location = StringField("Location", validators=[Optional(), Length(max=100)])
    vlan = StringField("VLAN", validators=[Optional(), Length(max=100)])
    purdue_level = SelectField("Purdue Level", choices=[
        ("", "Select a Purdue level"),
        ("0", "Level 0 - Physical process"),
        ("1", "Level 1 - Basic control"),
        ("2", "Level 2 - Supervisory control"),
        ("3", "Level 3 - Site operations"),
        ("3.5", "Level 3.5 - OT DMZ"),
        ("4", "Level 4 - Enterprise systems"),
        ("5", "Level 5 - External networks"),
    ], validators=[DataRequired()])
    
    zone = SelectField("Zone", choices=[
        ("", "Select a zone"),
        ("Safety Zone", "Safety Zone"),
        ("Cell/Area Zone", "Cell/Area Zone"),
        ("Supervisory Control Zone", "Supervisory Control Zone"),
        ("Site Operations Zone", "Site Operations Zone"),
        ("OT DMZ", "OT DMZ"),
        ("Enterprise Zone", "Enterprise Zone"),
        ("External Zone", "External Zone"),
    ], validators=[DataRequired()])

    status = SelectField("Status", choices=[
        ("active", "Actvie"),
        ("inactive", "Inactive"),
        ("maintenance", "Maintenance"),
        ("decommissioned", "Decommissioned")
    ], default="active", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Save device")
    


class InitialAdminForm(FlaskForm):

    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=12, max=128)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Create Administrator")


class LoginForm(FlaskForm):

    email = StringField("Email Address", validators=[DataRequired(),Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    remember_me = BooleanField("Keep me signed in" )
    submit = SubmitField("Sign in")


class LogoutForm(FlaskForm):

    submit = SubmitField("Sign out")



class CreateUserForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(max=100),
        ],
    )

    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )

    role = SelectField(
        "Role",
        choices=[
            ("viewer", "Viewer"),
            ("editor", "Editor"),
            ("admin", "Administrator"),
        ],
        validators=[DataRequired()],
    )

    password = PasswordField(
        "Temporary password",
        validators=[
            DataRequired(),
            Length(min=12, max=128),
        ],
    )

    confirm_password = PasswordField(
        "Confirm temporary password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    submit = SubmitField("Create user")


    
