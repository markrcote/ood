You need [Vagrant][] and a Vagrant provider like [VirtualBox][].  You
also need the Vagrant plugin for VirtualBox Guest Additions:

    $ vagrant plugin install vagrant-vbguest

Ansible is also required.  If you aren't already in a virtualenv,
create one in the testing/ directory and install ansible:

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install ansible

Set up a local config, by editing ood/settings_local.py and adding

    SECRET_KEY = <string>

where `<string>` should be a long random string.

You probably want these settings too:

    DEBUG = True
    UPDATE_STATE_PERIOD_SECONDS = 10

Start up the machine with Vagrant:

    cd testing
    vagrant up

ssh into the machine:

    vagrant ssh

Load the virtualenv:

    cd /srv/ood
    . venv/bin/activate
    cd ood

Create an admin account:

    python manage.py createsuperuser

Start up the development server:

    python manage.py runserver 0.0.0.0:8000

Port 8000 is forwarded to the host's localhost interface, so you can
access the ood instance by loading http://localhost:8000/ in your
browser.

[Vagrant]: https://www.vagrantup.com/
[VirtualBox]: https://www.virtualbox.org/
