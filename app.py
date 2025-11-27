import requests
import sqlite3
import datetime
import os

DB = 'cloudflare_ips.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS ips (
              cidr TEXT PRIMARY KEY,
              last_seen DATE)""")
    conn.commit()
    conn.close()

def fetch_ips():
    r = requests.get("https://api.cloudflare.com/client/v4/ips")
    if r.status_code == 200:
        data = r.json()
        return data["result"]["ipv4_cidrs"]
    else:
        raise RuntimeError(f"Failed to fetch IPs: {r.status_code} {r.text}")

def check_changes(ips):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Get current DB entries
    c.execute("SELECT cidr FROM ips")
    old = {row[0] for row in c.fetchall()}

    new = set(ips)

    added = new - old
    removed = old - new

    # Update DB
    today = datetime.date.today().isoformat()
    for cidr in new:
        c.execute("INSERT OR REPLACE INTO ips (cidr, last_seen) VALUES (?, ?)", (cidr, today))
    conn.commit()
    conn.close()

    return notify(added, removed)

def notify(added, removed):
    user_key = os.environ.get("PO_USER_KEY") # Retrieve or None
    app_key = os.environ.get("PO_APP_KEY") # Retrieve or None
    if added or removed:
        msg = f"Clodflare IPs Changed!\nAdded {added}\nRemoved: {removed}"
        resp = requests.post("https://api.pushover.net/1/messages.json",
                             data = {
                                 "token": app_key,
                                 "user": user_key,
                                 "message": msg,
                                 "title": "Cloudflare IP Update"
                             })
        if resp.status_code != 200:
            print("Failed to send Pushover Notification:", resp.text)

if __name__ == "__main__":
    init_db()
    ips = fetch_ips()
    added, removed = check_changes(ips)
    notify(added, removed)
