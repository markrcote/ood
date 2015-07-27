# OoD: Ore on Demand

OoD is a system that creates a Minecraft server on demand and archives
and destroys it when is no longer in use.

OoD will also be a simple web app that allows authorized users to start and
stop the game.

The primary audience for OoD is a small group of casual Minecrafters, for
which a dedicated server would sit idle most of the time.  OoD minimizes
this idle time, greatly reducing the cost of running a server.

For example, a 1 GB droplet normally costs $10/month.  If the server only
gets used 10 hours a week, OoD would reduce this cost to less than $0.70/month,
including the idle period before OoD decides to shut down the server.  This
also makes it much more affordable to go with a heavier server, if desired. A
4 GB/2 CPU system would cost less than $3/month with the same usage.

When a user wants to play, they log into the web app.  If the server
is already running, the IP is displayed.  If not, they can start up
the server from the previous archive.  After a certain amount of time
without players, the host is archived and destroyed.

## Status

OoD is in the early stages.

* Host controller: core is functional; celery tasks to control it.
* Web app: not started.
* Droplet creation: not started.

### 2015/07/26

Playing with [Celery][], which looks like the best way to run
DropletController.  We can have a scheduled task that calls
DropletController.update_state() periodically, although this probably
makes state-dependent timeouts more important.

Starting to wonder if I really should take mozpool's
complex-yet-straightforward [state machine code][]...

*Later that day...*

I've now got a Celery app with tasks `update_state()`, `start()`, and
`stop()`.   It updates the state every minute, which is probably too long in
some cases to see all the state transitions.

To start the worker:

    celery -A ood worker -l info -B

Then in a Python interpreter you can start up the process:

    >>> from ood.tasks import start
    >>> start.delay()

The Minecraft server's IP and port are logged and also writted to
`~/.ood/minecraft_address`.

After 15 minutes (by default) without a player, the next worker call
to `update_state()` will begin the shutdown and archiving procedures.
You can also manually shut it down with

    >>> from ood.tasks import stop
    >>> stop.delay()

I had to quickly make all DropletController state persistent, since
an instance is freshly created at the beginning of each task.  It's super
ugly right now because I stashed things into temporary files (and in a
different way from the pre-existing `state` file).  This stuff should
probably all go into a database.  Since the web app will probably be
Django-based, I'll move the state variables to the Django-app db later.

I still need to test interrupting the worker while it is in the middle
of all the different states to make sure it picks up the state
metadata correctly.  Probably need real tests in general.

A good test of the state machine, at least, once it is separated from
the Droplet interfacing details, would be to run Minecraft in a local
docker instance.

### 2015/07/26

I have the core host controller working, although it needs something to drive
it (`update_status()` every X minutes) and a way to accept commands (probably
a simple named queue, for now at least).

The system currently presumes the following:

* There is at least one snapshot of a Minecraft droplet named
  `ood-<timestamp>`, where `<timestamp>` is a standard UNIX timestamp in
  seconds.

* This image needs to be running Minecraft via supervisord under the
  name `minecraft`.  It needs to be running on the port specified in
  `ood.droplet.MINECRAFT_PORT`, and it needs RCON running on
  `ood.droplet.MINECRAFT_RCON_PORT`.  An RCON password should also be
  set to a random string.  Edit server.properties:

        server-port=<MINECRAFT_PORT>
        enable-rcon=true
        rcon.port=<MINECRAFT_RCON_PORT>
        rcon.password=<RCON password>

* The following files need to exist in `~/.ood`:
  * `droplet_key`: Contains a DigitalOcean [Personal Access Token][].
  * `rcon_pw`: Contains the RCON password set above.
  * `ssh_key` and `ssh_key.pub`: SSH keys for root access to the
  snapshotted image.

* You need [MCRcon][] installed in your virtualenv.  This project
 doesn't have a package, nor does it have a license, so I can't
 include it here.  Hopefully I won't need to write my own.

Eventually I'll build an ansible playbook to create an image from scratch.

If you have all that set up, you can use OoD like so:

    >>> import ood.test

    >>> dc = ood.test.new()
    2015-07-26 02:25:42:INFO:root:Droplet is not running.

    >>> dc.start(); dc.wait_for_state('running', timeout=300, sleep_time=5)
    2015-07-26 02:26:54:INFO:root:State changed from archived to restoring.
    2015-07-26 02:27:05:INFO:root:Still in state restoring...
    2015-07-26 02:27:16:INFO:root:Still in state restoring...
    2015-07-26 02:27:27:INFO:root:Still in state restoring...
    2015-07-26 02:27:38:INFO:root:Still in state restoring...
    2015-07-26 02:27:49:INFO:root:State changed from restoring to starting.
    2015-07-26 02:28:00:INFO:root:Still in state starting...
    2015-07-26 02:28:05:INFO:root:State changed from starting to running.
    2015-07-26 02:28:05:INFO:root:Minecraft available on <IP>:<port>.

    >>> dc.wait_for_state('archived', timeout=3000, sleep_time=30, update_time=30)
    2015-07-26 02:30:01:INFO:root:Still in state running...
    2015-07-26 02:30:31:INFO:root:Still in state running...
    2015-07-26 02:31:02:INFO:root:Still in state running...
    2015-07-26 02:31:32:INFO:root:Still in state running...
    2015-07-26 02:32:03:INFO:root:Still in state running...
    2015-07-26 02:32:34:INFO:root:Still in state running...
    2015-07-26 02:33:05:INFO:root:Still in state running...
    2015-07-26 02:33:35:INFO:root:No players for the last 305 seconds.
    2015-07-26 02:33:35:INFO:root:Shutting down host.
    2015-07-26 02:33:36:INFO:root:State changed from running to shutting_down.
    2015-07-26 02:34:06:INFO:root:State changed from shutting_down to snapshotting.
    2015-07-26 02:34:37:INFO:root:Still in state snapshotting...
    2015-07-26 02:36:10:INFO:root:Snapshot completed: droplet 6295938.
    2015-07-26 02:36:10:INFO:root:State changed from snapshotting to destroying.
    2015-07-26 02:36:41:INFO:root:State changed from destroying to archived.

The `DropletController` class could probably be split into at least two
classes, one for the state machine and one for the droplet/server/RCON
interfacing.  That would also allow other cloud providers to be added.

The system as a whole needs to be more configurable.

State variables should be moved from memory to a database so the
service can be gracefully restarted.

We need image management, at a minimum to clear out old snapshots.

## Crazy Ideas

Thanks to [quarry][], it should be possible to make a very simple
server that speaks enough of the Minecraft protocol to dispense with
the web app.  A separate service could display the current status of
the host (including if it's down).  Trying to log into the service
would start up the real host; when booted, the IP would be published
in the OoD's fake server.

Even better, we could dynamically update DNS so the user wouldn't have
to copy the IP address.  The utility of this feature would depend on
the time to update.

Craziest still, we could try just one DNS entry for both the OoD fake
server and the Minecraft droplet.  I have a feeling this wouldn't work
without restarting Minecraft, though, unless there's no IP caching
going on anywhere.  Two DNS entries maybe the best solution here.

It might be worth investigating this before even embarking on a web
server.  The critical element will be DNS update time; if we have to
copy & paste IP addresses, it's probably preferable to use a web app,
since copying text from the Minecraft server list seems to be disabled.

[Personal Access Token]: https://cloud.digitalocean.com/settings/applications
[MCRcon]: https://github.com/barneygale/MCRcon
[quarry]: https://github.com/barneygale/quarry
[state machine code]: https://github.com/djmitche/mozpool/blob/master/mozpool/statemachine.py
[Celery]: http://docs.celeryproject.org
