#!/bin/bash

# Grant X11 display access to local containers:
xhost +local:

# Check if the --gui or -g flag is passed:
if [[ "$1" == "--gui" || "$1" == "-g" ]]; then
    # Re-open just the GUI later (without re-importing):
    echo "Starting GUI only..."
    podman-compose up --no-deps busfactor
else
    # Build and run the full pipeline:
    echo "Building and running the full pipeline..."
    podman-compose up --build
fi
