# cielosoftBE
Backend

**********************
Run the application

python3 -m venv .venv

source .venv/bin/activate



pip install -r requirements.txt

python3 manage.py makemigrations

python3 manage.py migrate 

python3 manage.py runserver

python manage.py collectstatic

super user: python3 manage.py createsuperuser
