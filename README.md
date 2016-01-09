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


