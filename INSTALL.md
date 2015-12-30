Installing and configuring an OoD server
========================================

Setting up an OoD server consists of

* Installing the preqrequisites
* Installing the OoD server
* Setting up an OoD MineCraft instance

Installing the prerequisites
----------------------------

You'll need a MySQL database and a broker for [Celery][] (e.g. RabbitMQ).
Install those as per usual for your OS/distribution.  Other databases
will probably work as well, but MySQL support is installed by default
when OoD is installed.  You will also need the development files for
MySQL, e.g. `libmysqlclient-dev` on Ubuntu or `mysql-devel` on
Red-Hat-based distros.

Installing the OoD server
-------------------------

As with most Python apps, you should use a virtualenv to isolate OoD's
dependencies from other Python packages.  There are different ways to
structure your installation, such as creating the virtualenv and then
putting OoD's source into a subdirectory within the virtualenv, e.g.
`src/ood`, or checking out the source and then creating the virtualenv
within the working directory, e.g. in `venv/`.

These instructions are for the former method:

    ood@ubuntu:~$ virtualenv ood
    Running virtualenv with interpreter /usr/bin/python2
    New python executable in ood/bin/python2
    Also creating executable in ood/bin/python
    Installing setuptools, pip...done.

Load the virtualenv and check out the code:

    ood@ubuntu:~$ cd ood
    ood@ubuntu:~/ood$ . bin/activate
    (ood)ood@ubuntu:~/ood$ mkdir src
    (ood)ood@ubuntu:~/ood$ cd src
    (ood)ood@ubuntu:~/ood/src$ git clone https://github.com/markrcote/ood
    Cloning into 'ood'...
    remote: Counting objects: 218, done.
    remote: Compressing objects: 100% (21/21), done.
    remote: Total 218 (delta 7), reused 0 (delta 0), pack-reused 196
    Receiving objects: 100% (218/218), 55.71 KiB | 0 bytes/s, done.
    Resolving deltas: 100% (104/104), done.
    Checking connectivity... done.


Finally, install the requirements:

    (ood)ood@ubuntu:~/ood/src$ cd ood
    (ood)ood@ubuntu:~/ood/src/ood$ pip install -r requirements.txt
    Downloading/unpacking amqp==1.4.6 (from -r requirements.txt (line 1))
    ...

A whole lot of stuff will be printed out after that.  If everything worked,
you should see `Successfully installed`, with a list of package names,
near the end out of the output.

You're now ready to set up the application, starting with the settings
file.

A bunch of defaults are in `ood/settings.py`.  All settings there are
overridden by `ood/settings_local.py`, if it exists.  Most of the
defaults should be fine, but there are a few you'll need to change,
and a few you may want to.

You'll need to override `SECRET_KEY` to some unique string.  You can
use a [few Python commands][] to generate a good one.

If you want to use Google auth for your users, you will also need to
provide `SOCIAL_AUTH_GOOGLE_PLUS_KEY` and
`SOCIAL_AUTH_GOOGLE_PLUS_SECRET`.

You may also want to override Celery settings (see section labelled
"Celery config" in `settings.py`) and `DATABASES`.

If this is a development installation, set `DEBUG = True`.  If not,
set `ALLOWED_HOSTS` to a list of supported hostnames,
e.g. `ALLOWED_HOSTS = ["ood.mydomain.com"]`, and `STATIC_ROOT` to the
full path to the `ood/static` directory (which you'll create below).

Create a database for OoD.  The default settings are a database called
`ood` owned by a user called `ood`, with no password.  If you use the
default settings, ensure the `ood` user can only access MySQL via
localhost, since it has no password.  You can do that with

    mysql> create database ood;
    Query OK, 1 row affected (0.00 sec)

    mysql> grant all on ood.* to 'ood'@'localhost';
    Query OK, 0 rows affected (0.00 sec)

    mysql> flush privileges;
    Query OK, 0 rows affected (0.00 sec)

Then create all the necessary tables:

    python manage.py migrate

For production, you'll need to get all the static files in one place
(see the `STATIC_ROOT` setting above):

    python manage.py collectstatic

Next, you need a Celery worker.  For testing, you can run one on the
command line:

    celery -A ood worker -l info -B

For production, you'll want to run it automatically, e.g. by
supervisord.  Here's an example supervisord config file, for a config
called `ood-worker`, which should be stored (in Ubuntu, at least) in
something like `/etc/supervisor/conf.d/ood-worker.conf`:

    [program:ood-worker]
    command=/home/ood/ood/bin/celery -A ood worker -l info -B
    directory=/home/ood/ood/src/ood
    user=ood
    redirect_stderr=true
    stdout_logfile=/home/ood/ood/log/ood-worker.stdout
    environment=HOME="/home/ood"

Finally, to run the web app, you can use the command line for testing:

    python manage.py runserver

For production, you'll need to use a proper web server, e.g. Apache.
This is out of scope for these docs, but you'll probably need to use
the provided WSGI file, `ood/wsgi.py`, and remember that the static
files are in `ood/static`.  You should run over HTTPS since users need
to log in to use the app.


[Celery]: http://docs.celeryproject.org/en/latest/index.html
[few Python commands]: http://stackoverflow.com/questions/4664724/distributing-django-projects-with-unique-secret-keys/16630719#16630719
