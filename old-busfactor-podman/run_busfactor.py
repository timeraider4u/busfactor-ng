import os
import glob
import time
import shutil
import subprocess

repo_url = os.environ.get("REPO_URL", "https://github.com")
repo_name = os.path.basename(repo_url.rstrip("/"))
if repo_name.endswith(".git"):
    repo_name = repo_name[:-4]

export_dir = os.path.join("/shared", repo_name)
repo_json = os.path.join(export_dir, "repo_data.json")

print("[*] Waiting for {}...".format(repo_json))
while not os.path.isfile(repo_json):
    time.sleep(2)

print("[*] Starting Bus Factor Analyzer GUI (select {} inside the tool)...".format(repo_json))
subprocess.call(["python", "/opt/busfactor/tool.py"], cwd="/opt/busfactor")

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

copied = 0
for json_file in glob.glob("/opt/busfactor/data/*.json"):
    shutil.copy2(json_file, export_dir)
    copied += 1

print("[+] Exported {} analysis JSON files to ./output/{}/".format(copied, repo_name))
