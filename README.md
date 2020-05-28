# Stock Footage Automator
Manage and make selling your stock footage easier with [Stock Footage Automator]("https://stock-footage-automator.herokuapp.com/")!

Hosted on [Heroku]("https://www.heroku.com/")

## Setup
### Clone directory:
```
$ cd [workspace folder]
$ git clone https://github.com/kevinreber/Capstone-Project.git
```

### Create Python virtual environment:
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

### Setup database and populate:
```
(venv) $ createdb automator
(venv) $ python seed.py
```

### Start server:
```
(venv) $ flask run
```
Open http://localhost:5000/ to view project in the browser.


## Testing
```
(venv) $ python -m unittest [test_file]
```

## Built With
* [Axios]("https://github.com/axios/axios")
* [Flask]("https://flask.palletsprojects.com/en/1.1.x/")
* [WTForms]("https://wtforms.readthedocs.io/en/2.3.x/")
* [Flask SQLAlchemy]("https://flask-sqlalchemy.palletsprojects.com/en/2.x/")
* [PostgresSQL]("https://www.postgresql.org/")

## Styled With
* [Twitter Bootstrap]("https://getbootstrap.com/")
* [SASS]("https://sass-lang.com/install")

## Authors
* Kevin Reber - [Github]("https://github.com/kevinreber") - [Website]("https://www.kevinreber.dev/")