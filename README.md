# Skilled Hammer

[![Build Status](https://travis-ci.org/r00m/skilled-hammer.svg?branch=master)](https://travis-ci.org/r00m/skilled-hammer)

Simple deployments via GitHub's Webhooks

---

## Requirements

* Python 2.7 or 3.5
* Flask
* GitPython
* Gunicorn (optional)
* Supervisor (optional)
* NGINX (optional)

I say optional because they are not required to actually run the app, but they are needed when you deploy it in production.

For configuration examples see the `config` folder.

## Security

All incoming requests are validated according to [GitHub's Webhook guidelines](https://developer.github.com/webhooks/#payloads).

## Why?

I got sick of logging into the server, pulling code and running any additional commands thereafter.

## How?

When code is pushed to GitHub, GitHub then calls the URL where `Skilled Hammer` is listening on, which then takes care of pulling latest changes and running any additional commands like compiling sass, applying database migrations, copying static files or restarting services.

## How do I add a Webhook?

Go to the repository `Settings`, in the left side menu click on `Webhooks` and then click on `Add webhook` button.

The interesting bits here are:
- Payload URL - that's where `Skilled Hammer` is listening on
- Secret - this proves that request actually originated from GitHub's servers

Both need to be filled out!

## Installation

Easy mate, clone the repo and run:

```
$ pip install -r requirements.txt
```

all sorted!

**NB!** You should always use virtual environments (venv's) when installing python packages, [read on how and why](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

## Running

Copy example configuration and adjust it to your needs:

```
$ cp config/repositories.conf.example config/repositories.conf
```

For testing purposes you can use Flask's built-in development server:

```
$ python main.py
```

and navigate to http://127.0.0.1:5000, to see that it worked and GET method is not allowed :sweat_smile:

**NB!** For production deployments set `DEBUG = False`

**NB!** For production deployments you will need to setup a WSGI server that can talk to an HTTP server. Here's a [tutorial on setting up Gunicorn, Supervisor and NGINX](https://r00m.wordpress.com/2016/03/05/deploying-flask-nginx-gunicorn-supervisor-for-the-first-time/).

## Testing

```
$ python tests.py
```
