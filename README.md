# Skilled Hammer

[![Build Status](https://travis-ci.org/r00m/skilled-hammer.svg?branch=master)](https://travis-ci.org/r00m/skilled-hammer)

Simple deployments via GitHub's Webhooks

---

## Requirements

* Flask
* GitPython
* Gunicorn (optional)
* Supervisor (optional)
* NGINX (optional)

I say optional because they are not required to actually run the app, but they are needed when you deploy it in production.

## Installation

Easy mate, clone the repo and run:

```
$ pip install -r requirements.txt
```

all sorted!

**NB!** You should always use virtual environments (venv's) when installing python packages, [read on how and why](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

## Running

For testing purposes you can use Flask's built-in development server:

```
$ python3 skilled_hammer.py
```

and navigate to http://127.0.0.1:5000, to see that it worked and GET method is not allowed :sweat_smile:

**NB!** For production deployments you will need to setup a WSGI server that can talk to an HTTP server. Here's a [tutorial on setting up Gunicorn, Supervisor and NGINX](https://r00m.wordpress.com/2016/03/05/deploying-flask-nginx-gunicorn-supervisor-for-the-first-time/).

## Testing

```
$ python3 tests.py
```
