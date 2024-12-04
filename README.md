# Cyber-Prepa

## Table of contents

1. [App resume and structure](https://github.com/Proyectos-Especiales-CCM/Cyber-Prepa-Back/wiki/Structure)
2. [Development Setup](https://github.com/Proyectos-Especiales-CCM/Cyber-Prepa-Back/wiki/Development-Setup)
3. [Deployment (Windows)](#deployment-windows)
4. [Run as container (Linux Ubuntu)](#run-as-container-linux-ubuntu)
5. [To contribute to the project](https://github.com/Proyectos-Especiales-CCM/Cyber-Prepa-Back/wiki/Contribute)

## Deployment (Windows)

- Install [Python](https://www.python.org/downloads/)
- Install [Redis](https://redis.io/docs/install/install-redis/install-redis-on-windows/)

### Clone the project and install the dependencies

```bash
git clone
cd Cyber-Prepa
python -m venv .venv
.venv\Scripts\activate.ps1
pip install -r requirements.txt
```

### Install postgresql database

Install postgresql to host machine or Set a postgresql database on Cloud

```sql
CREATE DATABASE cyberprepa;
\c cyberprepa
CREATE USER cyberprepadbuser WITH PASSWORD 'cyberprepadbuserpassword';
GRANT ALL PRIVILEGES ON DATABASE cyberprepa TO cyberprepadbuser;
GRANT ALL PRIVILEGES ON SCHEMA public TO cyberprepadbuser;
```

### Generate the required environment variables and set DEBUG to False

In the settings.py file, set DEBUG to False.

```python
DEBUG = False
```

Then create a .env file and add the environment variables:

```bash
# This generates a secret key and prints it to the console
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

The .env file should look like this:

```dotenv
SECRET_KEY=2hb40lab4)zqt0zwt=m_q^q&m11ku)9*ky0)-6hkh3@4*uuwzm
CORS_ALLOWED_ORIGINS=http://localhost,http://192.168.0.1
ALLOWED_HOSTS=localhost,192.168.0.1 
```

### Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Deploy using daphne

```bash
daphne -b 0.0.0.0 -p 8001 main.asgi:application
```

### Initialize redis server or use a docker container

```bash
docker run --rm -p 6379:6379 redis:alpine
```

### Install IIS

- Search for "Turn Windows features on or off" in the start menu and open it.
- Scroll down and find "Internet Information Services" and check the box.
- Click OK and wait for the installation to complete.

### Configure IIS for media files

Add a virtual directory to the media folder in the IIS server.
Right-click on the default website and select "Add Virtual Directory".
Set the alias to "media" and the physical path to the media folder in the project.

It should look like this:

```plaintext
Alias: media
Physical path: C:\path\to\project\media
```

### Optional: Add SSL to the server

You can generate a self-signed certificate using openssl.
I recommend to use the Git Bash terminal, as git installation comes with an openssl binary. Locate the directory where you want to generate the certificate and run the following command at that directory in the Git Bash terminal.

```bash
openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out certificate.pem
```

Then run the server with SSL

```bash
daphne -e ssl:8001:privateKey=key.pem:certKey=certificate.pem main.asgi:application
```

## Run as container (Linux Ubuntu)

### Compoase build and run the container

Run the following command in terminal.

```bash
sudo docker compose up --build
```
