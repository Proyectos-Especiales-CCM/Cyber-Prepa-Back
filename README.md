# Cyber-Prepa

## App resume and guide
Please look at the [APP_GUIDE.md](APP_GUIDE.md) file for more information about how the app works.

## To clone & setup the project

### Clone the project and go to the project directory
```bash
git clone https://github.com/Dev-Society-CCM/Cyber-Prepa.git
cd Cyber-Prepa
```

### Create a virtual environment, activate it & install the dependencies
- Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
- Windows
```powershell
py -m venv .venv
.venv\Scripts\activate.ps1
pip install -r requirements.txt
```

### Generate a secret key and add it to the environment variables
- Linux
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
- Windows
```powershell
py -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Then add the generated key to the environment (.env file) variables as `SECRET_KEY`
Example:
SECRET_KEY=2hb40lab4)zqt0zwt=m_q^q&m11ku)9*ky0)-6hkh3@4*uuwzm

:exclamation: Don't push the .env file to the repository, it's already ignored in the .gitignore file & it contains sensitive data ! That's why is called SECRET_KEY :)

### Run the migrations and run the server
- Linux
```bash
python3 manage.py migrate
python3 manage.py runserver
```
- Windows
```powershell
py manage.py migrate
py manage.py runserver
```

## To contribute to the project

### Create a new branch
Change \<branch-name> to the name of the branch you want to create.
```bash
git checkout -b <branch-name>
```
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