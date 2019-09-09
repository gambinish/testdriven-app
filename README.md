### In manage.py:

* initialize db: `docker-compose exec users python manage.py recreate_db`

* seed db: `docker-compose exec users python manage.py seed_db`

* run tests: `docker-compose exec users python manage.py test`