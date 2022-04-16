# cielosoftBE
Backend

**********************
```Run the application

python3 -m venv .venv

source .venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt

# setup project
django-admin startproject bookhunt
python manage.py startapp example
python3 manage.py makemigrations
python3 manage.py migrate 
python3 manage.py runserver
python manage.py collectstatic

# create super user
super user: python3 manage.py createsuperuser

```
