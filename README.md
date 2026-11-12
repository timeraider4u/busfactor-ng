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

## Stop old busfactor GUI tool
```bash
cd ./old-busfactor-podman
./old-busfactor-podman/stop.sh
```
