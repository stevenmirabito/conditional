Conditional
===========

[![Build Status](https://travis-ci.org/ComputerScienceHouse/conditional.svg)](https://travis-ci.org/ComputerScienceHouse/conditional)

A comprehensive membership evaluations solution for Computer Science House.

Development
-----------

Install [Docker](https://www.docker.com/community-edition) if you don't already have it and add your LDAP bind credenticals in `.env`:

```
LDAP_BIND_DN=uid=[your CSH username],ou=Users,dc=csh,dc=rit,dc=edu
LDAP_BIND_PASSWORD=[your CSH password]
```

Then, simply run: `docker-compose up`

Once everything has started, navigate to [http://localhost:3000](http://localhost:3000). Any changes made to the frontend files in `frontend` or the Jinja templates in `conditional/templates` will cause the browser to reload automatically.

### Database Migrations

If you change the database schema, you must generate a new migration by running:

```
export FLASK_APP=app.py
flask db migrate
```

The new migration script in `migrations/versions` should be verified before being committed, as Alembic may not detect every change you make to the models.

For more information, refer to the [Flask-Migrate](https://flask-migrate.readthedocs.io/) documentation.

### Old Evals DB Migration

Conditional includes a utility to facilitate data migrations from the old Evals DB. This isn't necessary to run Conditional. To perform this migration, run the following commands before starting the application:

```
pip install pymysql
export FLASK_APP=app.py
flask zoo
```
