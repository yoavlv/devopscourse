#!/bin/bash

# Define the base directory where Tomcat folders are located (C:\ becomes /c in Git Bash or WSL)
BASE_DIR="/c"

# Look for directories that start with "apache-tomcat-"
TOMCAT_DIR=$(find "$BASE_DIR" -maxdepth 1 -type d -name "apache-tomcat-*")

# Check if we found any Tomcat directory
if [ -z "$TOMCAT_DIR" ]; then
    echo "No Apache Tomcat directory found under $BASE_DIR"
    exit 1
fi

# Output the found Tomcat directory
echo "Found Tomcat Directory: $TOMCAT_DIR"

# Change into its bin directory
cd "$TOMCAT_DIR/bin" || { echo "Failed to cd into $TOMCAT_DIR/bin"; exit 1; }

# Confirm we're in the right place
pwd
ls -la

# Run shutdown.bat and startup.bat
echo "Stopping Tomcat..."
cmd.exe /c shutdown.bat

echo "Waiting for Tomcat to stop..."
sleep 5

echo "Starting Tomcat..."
cmd.exe /c startup.bat

echo "Tomcat restarted successfully!"