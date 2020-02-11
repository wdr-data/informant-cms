web: gunicorn --chdir app main.wsgi -k sync --log-file -
release: python app/manage.py migrate
