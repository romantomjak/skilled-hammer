# Skilled Hammer

[![Build Status](https://travis-ci.org/r00m/skilled-hammer.svg?branch=master)](https://travis-ci.org/r00m/skilled-hammer)

Simple GitHub/Bitbucket Webhook deployments (with [Slack integration](#slack-integration) :tada:)

---

## Requirements

* Docker

## Why did you create this?

Does this look familiar?

```
$ git commit -am "FIYAAA :fire:"
$ ssh dev
$ cd /var/www/my-project
$ git pull origin develop
$ [touch app.wsgi | cp -R dist/ public_html/ | ... ]
```

Woudn't it be nice if you could just `commit`, `push` and get notified in [Slack](https://slack.com) once the change is deployed?

## How does this work?

You will need to setup a [Webhook](https://en.wikipedia.org/wiki/Webhook) that will get triggered every time you push a code change to [GitHub](https://github.com) / [Bitbucket](https://bitbucket.org). 

`Skilled Hammer` will then take care of pulling the latest changes and running any additional commands you have defined. Usual suspects include:

- compiling sass
- applying database migrations
- copying static files
- restarting services

## How do I add a Webhook?

### GitHub

Go to the repository `Settings`, in the left side menu click on `Webhooks` and then click on `Add webhook` button.

The interesting bits here are:

- Payload URL - that's where `Skilled Hammer` is listening on
- Secret - this proves that request actually originated from GitHub's servers

Both need to be filled out!

### Bitbucket

Go to the repository `Settings`, in the secondary menu click on `Webhooks` and then click on `Add webhook` button.

## Configuration

Configuration is stored in `repositories.conf` and this is how an example entry would look like:

```
[vigilant-octo]
# the repository in question
origin = https://github.com/r00m/vigilant-octo

# working directory. this is where `git pull` and `command` are run from
directory = /var/www/vigilant-octo.org

# the command to run after a successfull `git pull`
command = compass compile
```

**NB!** The command you are executing must exist in the Docker container. See [Dockerfile reference](https://docs.docker.com/engine/reference/builder/) on how to modify it.

## Running

**NB!** Make sure you have edited your `repositories.conf` :eyes:

It's quite easy:

```
docker run --restart=unless-stopped --name skilled-hammer \
	-p "8000:8000" \
	-e "HAMMER_SECRET=YOUR_SECRET_HERE" \
	-v "$PWD/repositories.conf:/usr/src/app/repositories.conf" \
	skilled-hammer
```

and navigate to [http://localhost:8000](http://localhost:8000), to see that it worked and GET method is not allowed :sweat_smile:

### Slack integration

Just add `SLACK_HOOK` environment variable:

```
docker run --restart=unless-stopped --name skilled-hammer \
	-p "8000:8000" \
	-e "HAMMER_SECRET=YOUR_SECRET_HERE" \
	-e "SLACK_HOOK= YOUR_HOOK_URL_HERE" \
	-v "$PWD/repositories.conf:/usr/src/app/repositories.conf" \
	skilled-hammer
```

## Testing

```
$ docker run skilled-hammer python skilled_hammer/tests.py
```

## Security

All incoming requests are validated according to [GitHub's Webhook guidelines](https://developer.github.com/webhooks/#payloads) or [Bitbucket's Event Payloads](https://confluence.atlassian.com/bitbucket/event-payloads-740262817.html).

**NB!** For projects hosted on GitHub, always setup `Secret` when creating a Webhook, it provides additional layer of security.

## License

MIT
