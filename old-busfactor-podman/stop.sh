#!/bin/bash

# Stop compose stack
podman-compose down

# Remove X11 display access to local containers:
xhost -local:
