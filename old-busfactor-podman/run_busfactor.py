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
html_dir = os.path.join(export_dir, "html")
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

if os.path.exists(html_dir):
    shutil.rmtree(html_dir)
os.makedirs(html_dir)

shutil.copy2("/opt/busfactor/index.html", html_dir)
for folder in ("css", "js", "data"):
    src = os.path.join("/opt/busfactor", folder)
    dst = os.path.join(html_dir, folder)
    if os.path.isdir(src):
        shutil.copytree(src, dst)

print("[+] Exported {} analysis JSON files to ./output/{}/".format(copied, repo_name))
print("[+] Exported standalone HTML viewer to ./output/{}/html/index.html".format(repo_name))
