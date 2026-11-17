# busfactor-ng
Modernize https://github.com/SOM-Research/busfactor

## How-to run old busfactor GUI tool inside podman (on Linux Mint)
Running the old `python 2.7` GUI tool from https://github.com/SOM-Research/busfactor.git
```bash
cd ./old-busfactor-podman
./start.sh
```

- Using Podman under `Linux Mint 22 Zena`.
- As `Busfactor` uses an old `python 2.7` GUI framework, wee need to pass `X11` socket
into Podman container.

What podman compose stack will do:
1. `podman-compose` will clone git repository configured in [.env file](./old-busfactor-podman/.env) into Docker volume
1. `podman-compose` will then import git repository with the help of `Gitana` and [gitana_extract.py](./old-busfactor-podman/gitana_extract.py) python script into a MySQL/MariaDB database
1. `Gitana` will then then extract a temporary JSON file.
1. `Busfactor GUI` will then be started
1. Select JSON file in GUI window/dialog, e.g., `/shared/repo_data.json`
1. Leave the values as-is
1. Click `Execute` button
1. It should open an `index.html` page inside a `Chromium` web-browser
1. Log outputs should be:
    ```
    ...
    2026-11-17T02:03:34.817801Z 0 [Note] mysqld: ready for connections.
    Version: '5.7.44'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server (GPL)
    podman start -a busfactor_cloner
    [cloner]    | [*] Cleaning up previous workspace directories...
    [cloner]    | [*] Using shallow clone depth: 500
    [cloner]    | [*] Cloning branch '9.2.x' of https://github.com/pytest-dev/pytest.git...
    Cloning into '/workspace/repo.tmp'...
    podman start -a busfactor_gitana
    [gitana]    | [*] Waiting for git clone to finish...
    podman start -a busfactor_gui
    [cloner]    | [*] Moving completed clone to /workspace/repo...
    [cloner]    | [+] Repository cloned successfully.
    exit code: 0
    /usr/local/lib/python2.7/site-packages/BeautifulSoup.py:114: UserWarning: You are using a very old release of Beautiful Soup, last updated in 2011. If you installed the 'beautifulsoup' package through pip, you should know the 'beautifulsoup' package name is about to be reclaimed by a more recent version of Beautiful Soup which is incompatible with this version.

    This will happen at some point after January 1, 2021.

    If you just started this project, this is easy to fix. Install the 'beautifulsoup4' package instead of 'beautifulsoup' and start using Beautiful Soup 4.

    If this is an existing project that depends on Beautiful Soup 3, the project maintainer (potentially you) needs to start the process of migrating to Beautiful Soup 4. This should be a relatively easy part of the Python 3 migration.

    """)
    [gitana]    | [*] Verified branch/reference 'origin/9.2.x' exists in /workspace/repo.
    [gitana]    | [*] Waiting for MySQL database 'db' to become reachable...
    2026-11-17T02:03:45.324279Z 3 [Note] Got an error reading communication packets
    [gitana]    | [*] Connecting to MySQL (10.89.3.88) and initializing Gitana database...
    [gitana]    | [*] Importing Git repository data into MySQL (total commits in repo: 4270)...
    [gitana]    | [*] Import progress: 23/4270 commits (0.5%) | 4.6 commits/s | ETA ~15m 25s
    [gitana]    | [*] Import progress: 35/4270 commits (0.8%) | 3.5 commits/s | ETA ~20m 12s
    ...
    [gitana]    | [*] Exporting JSON for branch 'origin/9.2.x' to /shared/pytest/repo_data.json...
    [gitana]    | [+] Gitana extraction finished successfully (50515062 bytes).
    exit code: 0
    127.0.0.1 - - [17/Nov/2026 02:53:55] "GET /index.html HTTP/1.1" 200 -
    ...
    127.0.0.1 - - [17/Nov/2026 02:53:56] "GET /data/extension_relevance.json HTTP/1.1" 200 -
    [busfactor] | Starting server...
    [busfactor] | Shutting down server...
    [busfactor] | [*] Waiting for /shared/pytest/repo_data.json...
    [busfactor] | [*] Starting Bus Factor Analyzer GUI (select /shared/pytest/repo_data.json inside the tool)...
    [busfactor] | [+] Exported 6 analysis JSON files to ./output/pytest/
    [busfactor] | [+] Exported standalone HTML viewer to ./output/pytest/html/index.html
    exit code: 0
    ...
    ```
1. You can find exported JSON files and HTML report inside `output` sub-directories.

## How-to run old busfactor GUI tool inside podman (on Linux Mint) - for a different git repository:
Adjust `old-busfactor-podman/.env` file, e.g.,
```env
REPO_URL=https://github.com/pytest-dev/pytest.git
BRANCH_NAME=origin/9.2.x
CLONE_DEPTH=500
```

## Stop old busfactor GUI tool
```bash
cd ./old-busfactor-podman
./old-busfactor-podman/stop.sh
```
