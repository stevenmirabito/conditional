Conditional
===========

[![Build Status](https://travis-ci.org/ComputerScienceHouse/conditional.svg)](https://travis-ci.org/ComputerScienceHouse/conditional) [![All Contributors](https://img.shields.io/badge/all_contributors-10-orange.svg?style=flat-square)](#contributors)

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

## Contributors

Thanks goes to these wonderful people ([emoji key](https://github.com/kentcdodds/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
| [<img src="https://avatars0.githubusercontent.com/u/3920942?v=3" width="100px;"/><br /><sub>Liam Middlebrook</sub>](http://liammiddlebrook.me)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=liam-middlebrook "Code") [🐛](https://github.com/ComputerScienceHouse/conditional/issues?q=author%3Aliam-middlebrook "Bug reports") [🚇](#infra-liam-middlebrook "Infrastructure (Hosting, Build-Tools, etc)") [📢](#talk-liam-middlebrook "Talks") [👀](#review-liam-middlebrook "Reviewed Pull Requests") | [<img src="https://avatars2.githubusercontent.com/u/8651166?v=3" width="100px;"/><br /><sub>Marc Billow</sub>](http://www.marcbillow.com)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=mbillow "Code") [🐛](https://github.com/ComputerScienceHouse/conditional/issues?q=author%3Ambillow "Bug reports") [👀](#review-mbillow "Reviewed Pull Requests") [🎨](#design-mbillow "Design") | [<img src="https://avatars1.githubusercontent.com/u/704880?v=3" width="100px;"/><br /><sub>Steven Mirabito</sub>](http://stevenmirabito.com/)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=stevenmirabito "Code") [🐛](https://github.com/ComputerScienceHouse/conditional/issues?q=author%3Astevenmirabito "Bug reports") [🔧](#tool-stevenmirabito "Tools") [🚇](#infra-stevenmirabito "Infrastructure (Hosting, Build-Tools, etc)") [👀](#review-stevenmirabito "Reviewed Pull Requests") [🎨](#design-stevenmirabito "Design") | [<img src="https://avatars2.githubusercontent.com/u/1261595?v=3" width="100px;"/><br /><sub>James Forcier</sub>](http://csssuf.net)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=csssuf "Code") | [<img src="https://avatars3.githubusercontent.com/u/5818258?v=3" width="100px;"/><br /><sub>Ram Zallan</sub>](http://ramzallan.me)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=RamZallan "Code") [🎨](#design-RamZallan "Design") | [<img src="https://avatars3.githubusercontent.com/u/2976769?v=3" width="100px;"/><br /><sub>Tal Cohen</sub>](https://github.com/TalCohen)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=TalCohen "Code") [🐛](https://github.com/ComputerScienceHouse/conditional/issues?q=author%3ATalCohen "Bug reports") [💬](#question-TalCohen "Answering Questions") | [<img src="https://avatars3.githubusercontent.com/u/3893578?v=3" width="100px;"/><br /><sub>Brandon Hudson</sub>](https://github.com/brandonhudson)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=brandonhudson "Code") [🎨](#design-brandonhudson "Design") |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| [<img src="https://avatars2.githubusercontent.com/u/2430381?v=3" width="100px;"/><br /><sub>Ryan Castner</sub>](http://audiolion.github.io)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=audiolion "Code") [🐛](https://github.com/ComputerScienceHouse/conditional/issues?q=author%3Aaudiolion "Bug reports") | [<img src="https://avatars3.githubusercontent.com/u/1441807?v=3" width="100px;"/><br /><sub>Stuart Olivera</sub>](https://stuartolivera.com)<br />[💻](https://github.com/ComputerScienceHouse/conditional/commits?author=sman591 "Code") | [<img src="https://avatars0.githubusercontent.com/u/14284544?v=3" width="100px;"/><br /><sub>Meghan Good</sub>](https://github.com/mgood15)<br />[💬](#question-mgood15 "Answering Questions") |
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/kentcdodds/all-contributors) specification. Contributions of any kind welcome!