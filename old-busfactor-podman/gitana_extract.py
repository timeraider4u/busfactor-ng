import os
import time
import shutil
import socket
import mysql.connector
from gitana.gitana import Gitana

branch = os.environ.get("BRANCH_NAME", "origin/master")

print("[*] Waiting for MySQL database 'db' to become reachable...")
while True:
    try:
        db_ip = socket.gethostbyname("db")
        sock = socket.create_connection((db_ip, 3306), timeout=2)
        sock.close()
        conn = mysql.connector.connect(user='root', password='root', host=db_ip, port=3306)
        cursor = conn.cursor()
        cursor.execute("DROP DATABASE IF EXISTS bus_factor_db;")
        conn.commit()
        cursor.close()
        conn.close()
        break
    except Exception:
        time.sleep(2)

CONFIG = {
    'user': 'root',
    'password': 'root',
    'host': db_ip,
    'port': '3306',
    'raise_on_warnings': False,
    'buffered': True
}

print("[*] Connecting to MySQL ({}) and initializing Gitana database...".format(db_ip))
g = Gitana(CONFIG)
g.init_db("bus_factor_db")
g.create_project("bus_factor_db", "target_project")

print("[*] Importing Git repository data into MySQL...")
g.import_git_data("bus_factor_db", "target_project", "target_repo", "/workspace/repo")

tmp_json = "/shared/repo_data.json.tmp"
final_json = "/shared/repo_data.json"
if os.path.exists(tmp_json):
    os.remove(tmp_json)
if os.path.exists(final_json):
    os.remove(final_json)

print("[*] Exporting JSON for branch: {}...".format(branch))
g.export_json("bus_factor_db", "target_repo", tmp_json, references=[branch])

if os.path.getsize(tmp_json) == 0:
    raise RuntimeError("Exported JSON is empty! Check BRANCH_NAME or MySQL sql-mode.")

shutil.move(tmp_json, final_json)
print("[+] Gitana extraction finished successfully ({} bytes).".format(os.path.getsize(final_json)))
