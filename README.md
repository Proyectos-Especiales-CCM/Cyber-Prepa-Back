# Cyber-Prepa

<style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .label {
        color: white;
        border-radius: 8px;
        padding: 2px 10px;
        font-size: 14px;
    }
</style>

## App resume and guide
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
- Redis server :bangbang:
- Nginx :bangbang:

:bangbang: - You can run it on a **docker container**. In that case, **docker** is required and **docker-compose** is optional.

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
curl -L https://gist.githubusercontent.com/Djmr5/19e2c8dd2480992500d12fd54a10913c/raw/e85561a2a65247aea28992558052a748da7aa6c7/myapp.conf -o /etc/nginx/sites-available/myapp.conf

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

## To contribute to the project

### Create a new branch
Change \<branch-name> to the name of the branch you want to create.
```bash
git checkout -b <branch-name>
```

Please follow the following naming convention for your branches so the github actions can work properly and label the pull requests accordingly.


`feature/user-authentication` **or**
`feat/chat-groups`
<p class="center"><span class="label" style="background-color: #183D07; border: 1.5px solid #4FB916;">feature</span></p>

`bug/fix-header-styling` **or**
`hotfix/security-patch` **or**
`fix/fix-login-redirect`
<p class="center"><span class="label" style="background-color: #5F0000; border: 1.5px solid red;">bug</span></p>

`docs/update-readme` **or** `documentation/add-documentation` **or** `doc/add-new-guide`
<p class="center"><span class="label" style="background-color: #003E6B; border: 1.5px solid #0075CA;">documentation</span></p>

`style/update-styles` **or** `frontend/add-styles` **or** `ui/add-new-component` **or** `ux/add-new-animation`
<p class="center"><span class="label" style="background-color: #782306; border: 1.5px solid #D93F0B;">frontend</span></p>

`enhancement/add-new-feature` **or** `enhance/improve-feature`
<p class="center"><span class="label" style="background-color: #5e8c8c; border: 1.5px solid #A2EEEF;">enhancement</span></p>


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