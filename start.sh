#!/bin/bash
PROJECT_DIR="/Users/macintosh/Documents/SEMESTER 5/GRAFIKA KOMPUTER/UAS"
cd "$PROJECT_DIR"

if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
    echo "Installing dependencies..."
    ./env/bin/pip install pygame PyOpenGL PyOpenGL_accelerate numpy
fi

echo "Starting Boat Simulation..."
./env/bin/python main.py
