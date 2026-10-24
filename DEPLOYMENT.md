# Deploying OT Inventory to PythonAnywhere

These instructions target the PythonAnywhere account `assetslab` and the public
address `https://assetslab.pythonanywhere.com`.

## 1. Copy the application from GitHub

Open a Bash console in PythonAnywhere and run:

```bash
cd ~
git clone YOUR_GITHUB_REPOSITORY_URL OT-Inventory-1.0
cd OT-Inventory-1.0
```

For a private repository, configure GitHub authentication first. Do not put a
GitHub token in the repository or in a command that will remain in shell
history.

## 2. Create the Python environment

Use the same Python version for the virtual environment and the web app:

```bash
mkvirtualenv --python=/usr/bin/python3.13 ot-inventory
pip install -r ~/OT-Inventory-1.0/requirements.txt
```

## 3. Create the web app

On the PythonAnywhere **Web** page:

1. Select **Add a new web app**.
2. Select **Manual configuration**.
3. Select Python 3.13 (or the version used for the virtual environment).
4. Set the virtualenv to `/home/assetslab/.virtualenvs/ot-inventory`.

Replace the contents of the generated WSGI configuration file with:

```python
import os
import sys

project_path = "/home/assetslab/OT-Inventory-1.0"
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ["SECRET_KEY"] = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
os.environ["DATABASE_URI"] = "sqlite:////home/assetslab/OT-Inventory-1.0/instance/inventory.db"

from run import app as application
```

Generate the secret in the Bash console with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Store the generated value only in the private WSGI configuration. Never commit
it to GitHub.

## 4. Configure static files

On the **Web** page, add this static-files mapping:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/assetslab/OT-Inventory-1.0/static/` |

## 5. Create the production database

In the Bash console:

```bash
cd ~/OT-Inventory-1.0
workon ot-inventory
export DATABASE_URI='sqlite:////home/assetslab/OT-Inventory-1.0/instance/inventory.db'
flask --app run.py db upgrade
```

Do not upload the development database or its backups. They may contain asset
and user information and should remain outside Git.

## 6. Publish and create the administrator

Use **Reload** on the PythonAnywhere Web page, then visit:

`https://assetslab.pythonanywhere.com/setup`

Create the initial administrator immediately. Once any user exists, the setup
page returns a not-found response and cannot create another administrator.

## Updating the deployed application

After pushing an update to GitHub, run:

```bash
cd ~/OT-Inventory-1.0
git pull --ff-only
workon ot-inventory
pip install -r requirements.txt
export DATABASE_URI='sqlite:////home/assetslab/OT-Inventory-1.0/instance/inventory.db'
flask --app run.py db upgrade
```

Then use **Reload** on the PythonAnywhere Web page. GitHub is the source of the
code, but a normal PythonAnywhere deployment does not automatically redeploy
when a commit is pushed.
