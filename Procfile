web: gunicorn --chdir app main.wsgi --log-file -
release: python app/manage.py collectstatic --noinput --no-post-process && python app/manage.py migrate
