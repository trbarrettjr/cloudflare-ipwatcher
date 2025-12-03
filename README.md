# Quick Notes for Successful Usage

I use Pushover, and I wanted to be notified if Cloudflare made any changes to the IP base so that I can update my firewall.
I setup a cronjob to run once a day and notify me.

## Persistent Data

To persist the database, you need to first run: ```docker volume create cf-ipwatcher```
This volume will store the app and the sqlite3 database to monitor changes.

## Environmental Variable

I am not going to persist keys in the python code, so I setup environmental variables.  See example below

# Suggested commandline

```bash
docker run --rm -e PO_USER_KEY=[PUSHOVER USER KEY] -e PO_APP_KEY=[PUSHOVER APP KEY] -v cf-ipwatcher:/app cf-ipwatcher:latest
```

## What I did

Like I said I have this setup to run once a day, so I have a cronjob that looks something like this:

```bash
0 13 * * * /usr/bin/docker run --rm -e PO_USER_KEY=null -e PO_APP_KEY=null -v cf-ipwatcher:/app cf-ipwatcher:latest
```

I nulled my personal details for my protection.

So this will run everyday at 13:00 local time.  If there is a change it will send a pushover alert.  No change == No Alert!

I hope you get value and enjoy.

## Update

I found out that it has been a while since the IP ranges have been updated.  So... I changed the scheduling to once a week and also changed the "minute" that the docker runs so as to not beat down Cloudflare's API.

Do my crontab looks like

```shell
8 8 * * 3 /usr/bin/docker run --rm -e PO_USER_KEY=null -e PO_APP_KEY=null -v cf-ipwatcher:/app cf-ipwatcher:latest
```
