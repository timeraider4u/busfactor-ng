import os
from gitana.gitana import Gitana

branch = os.environ.get("BRANCH_NAME", "origin/master")

CONFIG = {
    'user': 'root',
    'password': 'root',
    'host': 'db',
    'port': '3306',
    'raise_on_warnings': False,
    'buffered': True
}

print("[*] Connecting to MySQL and initializing Gitana database...")
g = Gitana(CONFIG)
g.init_db("bus_factor_db")
g.create_project("bus_factor_db", "target_project")

print("[*] Importing Git repository data into MySQL...")
g.import_git_data("bus_factor_db", "target_project", "target_repo", "/workspace/repo/.git")

print("[*] Exporting JSON for branch: {}...".format(branch))
g.export_json("bus_factor_db", "target_repo", "/opt/busfactor/data/repo_data.json", references=[branch])
print("[+] Gitana extraction finished successfully.")
