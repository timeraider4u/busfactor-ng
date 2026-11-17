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
    podman start -a busfactor_cloner
    Cloning into '/workspace/repo'...
    podman start -a busfactor_gitana
    podman start -a busfactor_gui
    [busfactor] | [*] Waiting for repo_data.json...
    /usr/local/lib/python2.7/site-packages/BeautifulSoup.py:114: UserWarning: You are using a very old release of Beautiful Soup, last updated in 2011. If you installed the 'beautifulsoup' package through pip, you should know the 'beautifulsoup' package name is about to be reclaimed by a more recent version of Beautiful Soup which is incompatible with this version.

    This will happen at some point after January 1, 2021.

    If you just started this project, this is easy to fix. Install the 'beautifulsoup4' package instead of 'beautifulsoup' and start using Beautiful Soup 4.

    If this is an existing project that depends on Beautiful Soup 3, the project maintainer (potentially you) needs to start the process of migrating to Beautiful Soup 4. This should be a relatively easy part of the Python 3 migration.

    """)
    2026-11-12T04:24:40.234891Z 2 [Note] Got an error reading communication packets
    [gitana]    | [*] Waiting for MySQL database 'db' to become reachable...
    [gitana]    | [*] Connecting to MySQL (10.89.3.53) and initializing Gitana database...
    [gitana]    | [*] Importing Git repository data into MySQL...
    [gitana]    | [*] Exporting JSON for branch 'origin/master' to /shared/busfactor/repo_data.json...
    [gitana]    | [+] Gitana extraction finished successfully (46781 bytes).
    exit code: 0
    127.0.0.1 - - [16/Nov/2026 23:48:51] "GET /index.html HTTP/1.1" 200 -
    ...
    127.0.0.1 - - [16/Nov/2026 23:48:51] "GET /data/references.json HTTP/1.1" 404 -
    [busfactor] | Starting server...
    [busfactor] | Shutting down server...
    [busfactor] | [*] Waiting for /shared/busfactor/repo_data.json...
    [busfactor] | [*] Starting Bus Factor Analyzer GUI (select /shared/busfactor/repo_data.json inside the tool)...
    [busfactor] | [+] Exported 6 analysis JSON files to ./output/busfactor/
    [busfactor] | [+] Exported standalone HTML viewer to ./output/busfactor/html/index.html
    exit code: 0
    ...
    ```
1. You can find exported JSON files and HTML report inside `output` sub-directories.

## How-to run old busfactor GUI tool inside podman (on Linux Mint) - for a different git repository:
Adjust `old-busfactor-podman/.env` file, e.g.,
```env
REPO_URL=https://github.com/pytest-dev/pytest.git
BRANCH_NAME=9.2.x
CLONE_DEPTH=500
```

## Stop old busfactor GUI tool
```bash
cd ./old-busfactor-podman
./old-busfactor-podman/stop.sh
```
