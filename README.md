# Hashtag-Monitor [![Build Status](https://travis-ci.com/lccasagrande/Hashtag-Monitor.svg?branch=master)](https://travis-ci.com/lccasagrande/Hashtag-Monitor)

This repository contains a simple dashboard that lets you monitor your hashtags on Twitter.

![WebApp Demonstration](hashtag_monitor/apps/monitor/docs/demonstration.gif)

## Requirements

You'll need Python 3.7 and PostgreSQL to be able to run this project.

If you do not have Python installed yet, it is recommended that you install the [Anaconda distribution](https://www.anaconda.com/distribution/) of Python, which has almost all packages required in these projects. Otherwise, upgrade your python version to the required one.

PostgreSQL installation instructions can be found [here](https://www.postgresql.org/download/). This project runs the PostgreSQL version 10 on Ubuntu x64. Other versions and OS were not tested.

Moreover, you'll need to sign up on twitter to get access to their API. Check the instructions [here](https://developer.twitter.com/). To sum up, you must create an app and generate the keys and tokens.

## Instructions

1. Clone the repository and navigate to the downloaded folder:

```bash
git clone https://github.com/lccasagrande/Hashtag-Monitor.git
cd Hashtag-Monitor
```

2. Install the required packages:

```bash
pip install -e .
```

3. Setup the following environment variables:
    - SECRET_KEY: The [Django Secret Key](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key).
    - TWITTER_CONSUMER_KEY: The Twitter Consumer API key.
    - TWITTER_CONSUMER_SECRET: The Twitter Consumer API key secret.
    - TWITTER_ACCESS_TOKEN: The Twitter Access Token.
    - TWITTER_ACCESS_TOKEN_SECRET: The Twitter Access Token Secret.
    - TWEETER_SYNC_MINUTES: The time in minutes in which the app will synchronize with twitter.
    - CLEAN_TRASH_FROM_DB_EVERY: The time in minutes in which the app will remove trash from the database.
    - DB_USER: The Database Username.
    - DB_PASSWORD: The Database Password.
    - DB_HOST: The Database Host (i.e. localhost).
    - DB_PORT: The Database Port number.
    - DB_NAME: The Database Name.

    If you use [VSCode](https://code.visualstudio.com/), you can add these variables to the [launch configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations) on the "env" property.

4. Create Database Tables:

```bash
manage.py migrate
```

5. Run Tests:

```bash
manage.py test hashtag_monitor.apps.monitor
```

6. Start the app:

```bash
manage.py runserver --noreload
```

## Extra Instructions for Deploying to Heroku
If you intend to deploy this application to Heroku, it's highly recommended that you install the pgbouncer buildpack to handle the connections with the Database.

We use [apscheduler](https://apscheduler.readthedocs.io/en/latest/) to run tasks in the background to sync with Tweeter. Therefore, pgbouncer is necessary to not exceed the concurrency connections.
