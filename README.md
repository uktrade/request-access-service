# request-access-service
App for requesting access to our tools

## Overview


## Dependencies
Python 3.7.3
DIT Authbroker/staff-sso

## Setting up a local development environment
1. Clone this repository

2. Create a virtual environment

```bash
# the project root:
virtualenv --python=python3 env
```

3. Install dependencies with pip-sync: `pip install -r requirements.txt`

4.  Copy sample_env to .env

5.  Add authbroker, email template IDs and notify key configuration values to your .env file

6.  Run database migration: `./manage.py migrate`

7.  Pre-populate the defaults into DB `./manage.py pre_load_defaults`

8.  Start up the local webserver: `./manage.py runserver`

## Running the tests

From the project's root directory run `./manage.py test`
