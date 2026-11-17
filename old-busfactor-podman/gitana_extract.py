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

DB_NAME = "bus_factor_db"
PROJECT_NAME = "target_project"
REPO_ALIAS = "target_repo"
REPO_PATH = "/workspace/repo"


def log(message):
    print(message)
    sys.stdout.flush()


def get_export_paths(repo_url):
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

    return tmp_json, final_json


def validate_branch_exists(repo_path, branch):
    raw_refs = subprocess.check_output(
        ["git", "-C", repo_path, "show-ref"]
    ).decode("utf-8", "replace").splitlines()

    valid_gitana_refs = []
    for line in raw_refs:
        parts = line.split()
        if len(parts) < 2:
            continue
        ref = parts[1]
        if ref.startswith("refs/remotes/") and not ref.endswith("/HEAD"):
            valid_gitana_refs.append((ref[len("refs/remotes/"):], "branch"))
        elif ref.startswith("refs/tags/"):
            valid_gitana_refs.append((ref[len("refs/tags/"):], "tag"))

    valid_names = [name for name, _ in valid_gitana_refs]
    if branch not in valid_names:
        formatted = ", ".join(
            ["{} ({})".format(name, rtype) for name, rtype in sorted(valid_gitana_refs)]
        ) or "NONE"
        raise RuntimeError(
            "Branch/reference '{}' does not exist in cloned repo! Valid BRANCH_NAME values for Gitana: [{}]".format(
                branch, formatted
            )
        )

    log("[*] Verified branch/reference '{}' exists in {}.".format(branch, repo_path))


def wait_for_mysql_and_reset_db(db_host="db", db_port=3306):
    log("[*] Waiting for MySQL database '{}' to become reachable...".format(db_host))
    last_err = None
    while True:
        try:
            db_ip = socket.gethostbyname(db_host)
            sock = socket.create_connection((db_ip, db_port), timeout=2)
            sock.close()
            conn = mysql.connector.connect(user="root", password="root", host=db_ip, port=db_port)
            cursor = conn.cursor()
            cursor.execute("DROP DATABASE IF EXISTS {};".format(DB_NAME))
            conn.commit()
            cursor.close()
            conn.close()
            return db_ip
        except Exception as exc:
            if str(exc) != last_err:
                log("[!] Still waiting on MySQL: {}".format(exc))
                last_err = str(exc)
            time.sleep(2)


def get_commit_count_from_git(repo_path):
    try:
        output = subprocess.check_output(
            ["git", "-C", repo_path, "rev-list", "--all", "--count"]
        ).strip()
        return int(output)
    except Exception:
        return 0


def get_imported_commit_count(db_ip):
    conn = mysql.connector.connect(
        user="root", password="root", host=db_ip, port=3306, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM commit;")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else 0


def run_import_with_progress(gitana_client, db_ip, repo_path):
    total_commits = get_commit_count_from_git(repo_path)
    stop_event = threading.Event()
    start_time = time.time()

    def monitor():
        while not stop_event.wait(5.0):
            try:
                imported = get_imported_commit_count(db_ip)
                elapsed = max(time.time() - start_time, 1.0)
                rate = imported / elapsed
                if total_commits > 0:
                    pct = min(100.0, (float(imported) / total_commits) * 100.0)
                    eta = int((total_commits - imported) / rate) if rate > 0 else 0
                    log("[*] Import progress: {}/{} commits ({:.1f}%) | {:.1f} commits/s | ETA ~{}m {}s".format(
                        imported, total_commits, pct, rate, eta // 60, eta % 60
                    ))
                else:
                    log("[*] Import progress: {} commits imported ({:.1f} commits/s)".format(imported, rate))
            except Exception:
                pass

    log("[*] Importing Git repository data into MySQL (total commits in repo: {})...".format(total_commits))
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        gitana_client.import_git_data(DB_NAME, PROJECT_NAME, REPO_ALIAS, repo_path)
    finally:
        stop_event.set()
        monitor_thread.join(timeout=2.0)


def verify_import_succeeded(db_ip):
    if get_imported_commit_count(db_ip) > 0:
        return

    log_files = sorted(
        set(glob.glob("/app/logs/*") + glob.glob("/opt/Gitana/logs/*")),
        key=os.path.getmtime
    )
    log_output = []
    for log_file in log_files:
        if os.path.isfile(log_file):
            with open(log_file, "r") as handle:
                lines = handle.readlines()[-30:]
            log_output.append("=== {} ===\n{}".format(log_file, "".join(lines)))

    raise RuntimeError(
        "Gitana imported 0 commits into MySQL!\nGitana Logs:\n{}".format(
            "\n".join(log_output) if log_output else "No log files found."
        )
    )


def export_and_verify_json(gitana_client, db_ip, branch, tmp_json, final_json):
    log("[*] Exporting JSON for branch '{}' to {}...".format(branch, final_json))
    gitana_client.export_json(DB_NAME, REPO_ALIAS, tmp_json, references=[branch])

    if not os.path.exists(tmp_json) or os.path.getsize(tmp_json) == 0:
        conn = mysql.connector.connect(
            user="root", password="root", host=db_ip, port=3306, database=DB_NAME
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
    log("[+] Gitana extraction finished successfully ({} bytes).".format(os.path.getsize(final_json)))


def main():
    repo_url = os.environ.get("REPO_URL", "https://github.com")
    branch = os.environ.get("BRANCH_NAME", "origin/master")

    tmp_json, final_json = get_export_paths(repo_url)
    validate_branch_exists(REPO_PATH, branch)
    db_ip = wait_for_mysql_and_reset_db()

    config = {
        "user": "root",
        "password": "root",
        "host": db_ip,
        "port": "3306",
        "raise_on_warnings": False,
        "buffered": True,
    }

    log("[*] Connecting to MySQL ({}) and initializing Gitana database...".format(db_ip))
    gitana_client = Gitana(config)
    gitana_client.init_db(DB_NAME)
    gitana_client.create_project(DB_NAME, PROJECT_NAME)

    run_import_with_progress(gitana_client, db_ip, REPO_PATH)
    verify_import_succeeded(db_ip)
    export_and_verify_json(gitana_client, db_ip, branch, tmp_json, final_json)


if __name__ == "__main__":
    main()
