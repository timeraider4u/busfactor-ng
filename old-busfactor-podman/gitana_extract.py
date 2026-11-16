import os
import time
import shutil
import socket
import mysql.connector
from gitana.gitana import Gitana

repo_url = os.environ.get("REPO_URL", "https://github.com")
branch = os.environ.get("BRANCH_NAME", "origin/master")

repo_name = os.path.basename(repo_url.rstrip("/"))
if repo_name.endswith(".git"):
    repo_name = repo_name[:-4]

export_dir = os.path.join("/shared", repo_name)
if not os.path.exists(export_dir):
    os.makedirs(export_dir)

tmp_json = os.path.join(export_dir, "repo_data.json.tmp")
final_json = os.path.join(export_dir, "repo_data.json")

for path in (tmp_json, final_json):
    if os.path.exists(path):
        os.remove(path)

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

print("[*] Exporting JSON for branch '{}' to {}...".format(branch, final_json))
g.export_json("bus_factor_db", "target_repo", tmp_json, references=[branch])

if os.path.getsize(tmp_json) == 0:
    raise RuntimeError("Exported JSON is empty! Check BRANCH_NAME or MySQL sql-mode.")

shutil.move(tmp_json, final_json)
print("[+] Gitana extraction finished successfully ({} bytes).".format(os.path.getsize(final_json)))
