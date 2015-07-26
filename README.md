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

* Host controller: core is functional
* Web app: not started
* Droplet creation: not started

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

We need image management, at a minimum to clear out old snapshots.

[Personal Access Token]: https://cloud.digitalocean.com/settings/applications
[MCRcon]: https://github.com/barneygale/MCRcon
