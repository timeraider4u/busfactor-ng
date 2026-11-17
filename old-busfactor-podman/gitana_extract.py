import os
import sys
import glob
import time
import shutil
import socket
import threading
import subprocess
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
sys.stdout.flush()
last_err = None
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
    except Exception as e:
        if str(e) != last_err:
            print("[!] Still waiting on MySQL: {}".format(e))
            sys.stdout.flush()
            last_err = str(e)
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
sys.stdout.flush()
g = Gitana(CONFIG)
g.init_db("bus_factor_db")
g.create_project("bus_factor_db", "target_project")

try:
    total_commits = int(subprocess.check_output(
        ["git", "-C", "/workspace/repo", "rev-list", "--all", "--count"]
    ).strip())
except Exception:
    total_commits = 0

stop_monitor = threading.Event()
start_time = time.time()


def monitor_progress():
    while not stop_monitor.wait(5.0):
        try:
            m_conn = mysql.connector.connect(
                user='root',
                password='root',
                host=db_ip,
                port=3306,
                database='bus_factor_db'
            )
            m_cursor = m_conn.cursor()
            m_cursor.execute("SELECT COUNT(*) FROM commit;")
            row = m_cursor.fetchone()
            imported = row[0] if row else 0
            m_cursor.close()
            m_conn.close()

            elapsed = max(time.time() - start_time, 1.0)
            rate = imported / elapsed
            if total_commits > 0:
                pct = min(100.0, (float(imported) / total_commits) * 100.0)
                eta = int((total_commits - imported) / rate) if rate > 0 else 0
                print("[*] Import progress: {}/{} commits ({:.1f}%) | {:.1f} commits/s | ETA ~{}m {}s".format(
                    imported, total_commits, pct, rate, eta // 60, eta % 60
                ))
            else:
                print("[*] Import progress: {} commits imported ({:.1f} commits/s)".format(imported, rate))
            sys.stdout.flush()
        except Exception:
            pass


print("[*] Importing Git repository data into MySQL (total commits in repo: {})...".format(total_commits))
sys.stdout.flush()

monitor_thread = threading.Thread(target=monitor_progress)
monitor_thread.daemon = True
monitor_thread.start()

try:
    g.import_git_data("bus_factor_db", "target_project", "target_repo", "/workspace/repo")
finally:
    stop_monitor.set()
    monitor_thread.join(timeout=2.0)

conn = mysql.connector.connect(
    user='root',
    password='root',
    host=db_ip,
    port=3306,
    database='bus_factor_db'
)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM commit;")
row = cursor.fetchone()
commit_count = row[0] if row else 0
cursor.close()
conn.close()

if commit_count == 0:
    log_files = sorted(
        set(glob.glob("/app/logs/*") + glob.glob("/opt/Gitana/logs/*")),
        key=os.path.getmtime
    )
    log_output = []
    for lf in log_files:
        if os.path.isfile(lf):
            with open(lf, "r") as f:
                lines = f.readlines()[-30:]
            log_output.append("=== {} ===\n{}".format(lf, "".join(lines)))

    raise RuntimeError(
        "Gitana imported 0 commits into MySQL!\nGitana Logs:\n{}".format(
            "\n".join(log_output) if log_output else "No log files found."
        )
    )

print("[*] Exporting JSON for branch '{}' to {}...".format(branch, final_json))
sys.stdout.flush()
g.export_json("bus_factor_db", "target_repo", tmp_json, references=[branch])

if not os.path.exists(tmp_json) or os.path.getsize(tmp_json) == 0:
    conn = mysql.connector.connect(
        user='root',
        password='root',
        host=db_ip,
        port=3306,
        database='bus_factor_db'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT name, type FROM reference ORDER BY type, name;")
    refs = cursor.fetchall()
    cursor.close()
    conn.close()

    available = ", ".join(["{} ({})".format(name, ref_type) for name, ref_type in refs]) or "NONE"
    raise RuntimeError(
        "Exported JSON is empty for branch '{}'! Available references in DB: [{}]".format(branch, available)
    )

shutil.move(tmp_json, final_json)
print("[+] Gitana extraction finished successfully ({} bytes).".format(os.path.getsize(final_json)))
sys.stdout.flush()
