# Cyber-Prepa

## Table of contents

1. [App resume and guide](#app-resume-and-guide)
2. [Requirements](#requirements)
3. [To clone & setup the project](#to-clone--setup-the-project)
4. [Deployment (Windows)](#deployment-windows)
5. [To contribute to the project](#to-contribute-to-the-project)

## App resume and guide

This is the backend of the Cyber-Prepa app. It's a Django app that uses Django Rest Framework and Django Channels to provide a REST API and a WebSocket API.

Please look at the [APP_GUIDE.md](APP_GUIDE.md) file for more information about how the app works.

## Requirements

- Python 3
  - django
  - python-dotenv
  - djangorestframework
  - django-cors-headers
  - channels
  - channels-redis
  - daphne
- Nginx :heavy_exclamation_mark:
- Redis server :bangbang:

:bangbang: - You can run it on a **docker container**. In that case, **docker** is required and **docker-compose** is optional.
:heavy_exclamation_mark: - Only required if you want to use Nginx as a reverse proxy server. Preferably, use for linux deployment.

### Recommended setup

- Ubuntu 20.04

## To clone & setup the project

### Clone the project and go to the project directory

```bash
git clone https://github.com/Dev-Society-CCM/Cyber-Prepa.git
cd Cyber-Prepa
```

### Create a virtual environment, activate it & install the dependencies

- Linux bash

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Generate a secret key and add it to the environment variables

- Linux bash

```bash
# This generates a secret key and prints it to the console
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Then add the generated key to the environment (.env file) variables as `SECRET_KEY`
Example:
SECRET_KEY=2hb40lab4)zqt0zwt=m_q^q&m11ku)9*ky0)-6hkh3@4*uuwzm

```bash
# To automatically create the .env file and add the generated key to it
echo "SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
```

Also in case you want to debug the app, set the DEBUG environment variable to True.

```dotenv
DEBUG=True
```

And in case you want to use the react frontend, add the following environment variable to the .env file. Or if you want to use the frontend on a different server, add the server's address instead localhost.

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost
ALLOWED_HOSTS=localhost
```

:exclamation: Don't push the .env file to the repository, it's already ignored in the .gitignore file & it contains sensitive data ! That's why is called SECRET_KEY :)

### Run the migrations and the server

- Linux bash

```bash
python3 manage.py migrate
python3 manage.py runserver
```

### Initialize redis server

- Linux bash

```bash
# Install Redis server
sudo apt install redis-server

# Enable and start the Redis service
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

- :exclamation: **Only if redis server port is changed** :exclamation:

```bash
# The above command should have started the redis server at the default port 6379
# If you want to start it at a different port, use the following command
redis-server --port 6380
```

:bangbang: - If you're running the redis server on a docker container, you can:

```bash
docker run --rm -p 6379:6379 redis:7
```

### Configure nginx

- Linux bash

```bash
# Install nginx
sudo apt install nginx

# Create a new configuration file > This will create a new file called 
# myapp.conf in /etc/nginx/sites-available thourgh a curl request to a
# gist file located at the url below. 
sudo curl -L https://gist.githubusercontent.com/Djmr5/19e2c8dd2480992500d12fd54a10913c/raw/1ee7a905d4be9816ae3d84a90709a153f8ee8ba8/myapp.conf -o /etc/nginx/sites-available/myapp.conf

# Create a symbolic link to sites-enabled
sudo ln -s /etc/nginx/sites-available/myapp.conf /etc/nginx/sites-enabled/
    
# Remove default configuration
sudo rm /etc/nginx/sites-enabled/default
sudo rm /etc/nginx/sites-available/default
    
# Test nginx configuration & restart nginx to apply changes
sudo nginx -t
sudo service nginx restart
```

:bangbang: - Or you can use a docker container for nginx

- More instructions are missing but you can look on how to create a docker container for nginx and use the myapp.conf file as a configuration file.

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

### Deply using daphne

```bash
daphne -b 0.0.0.0 -p 8001 main.asgi:application
```

### Initialize redis server or use a docker container

```bash
docker run --rm -p 6379:6379 redis:7
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

## To contribute to the project

### Create a new branch

Change \<branch-name> to the name of the branch you want to create.

```bash
git checkout -b <branch-name>
```

Please follow the following naming convention for your branches so the github actions can work properly and label the pull requests accordingly.

`feature/user-authentication` **or**
`feat/chat-groups`

![feature label](https://img.shields.io/badge/feature-4FB916?style=for-the-badge)

`bug/fix-header-styling` **or**
`hotfix/security-patch` **or**
`fix/fix-login-redirect`

![bug label](https://img.shields.io/badge/bug-FF0000?style=for-the-badge)

`docs/update-readme` **or** `documentation/add-documentation` **or** `doc/add-new-guide`

![docs label](https://img.shields.io/badge/docs-0075CA?style=for-the-badge)

`style/update-styles` **or** `frontend/add-styles` **or** `ui/add-new-component` **or** `ux/add-new-animation`

![frontend label](https://img.shields.io/badge/frontend-D93F0B?style=for-the-badge)

`enhancement/add-new-feature` **or** `enhance/improve-feature`

![enhancement label](https://img.shields.io/badge/enhancement-A2EEEF?style=for-the-badge)

If already working on a remote branch, you can pull the latest changes from it and create your local branch.

```bash
git checkout -b <branch-name> origin/<branch-name>
```

### To commit and push your changes

Add your changes to the staging area, commit them with a meaningful message (try to relate your commits to an issue) and push them to the repo.

```bash
git add .
git commit -m "your message"
git push origin <branch-name>
```

- To address an issue on your commit message, use the following syntax.

```bash
git commit -m "partial progress on issue #<issue-number>"
```

- To close an issue on your commit message, use the following syntax.
  - Reserved words are: close, closes, closed, fix, fixes, fixed, resolve, resolves, resolved

```bash
git commit -m "<reserved-word> #<issue-number>"
```

### Please create a pull request

Then go to the repo and create a pull request, but wait for at least two reviews before merging your branch to the main branch.

### Be creative and share ideas :smile:

If you have a request or believe something can be improved, feel free to open an issue and discuss it with the team. The project is still in its early stages, so we're open to any suggestions.
