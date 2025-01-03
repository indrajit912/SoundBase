#!/bin/bash
#
# SoundBase Installation Script
#
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025
#
# Description:
# This script installs the SoundBase application by performing the following:
#   1. Verifying Python 3.6+ installation.
#   2. Setting up required directories and a virtual environment.
#   3. Installing dependencies and the SoundBase application.
#   4. Adding the virtual environment's binary directory to the system PATH.
#
# Usage:
# Run this script using:
#   ./install.sh
#
# Notes:
# - Ensure you have internet access during the installation.
# - After installation, restart your terminal or source the appropriate shell profile
#   (e.g., ~/.bashrc or ~/.zshrc) to apply PATH changes.
#
# Exit Codes:
# 0 - Success
# 1 - Python is not installed or version is below 3.6.
# 2 - Dependency installation or setup failure.
#

# Function to print messages
function print_message() {
    echo -e "\033[1;32m$1\033[0m"
}

# Check which OS platform is running
platform='unknown'
unamestr=$(uname)
if [ "$unamestr" = "Linux" ]; then
   platform='linux'
elif [ "$unamestr" = "Darwin" ]; then
   platform='macos'
fi

# Step 1: Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: 'soundbase' requires Python version >= 3.6. Please install Python 3.6 or higher and try again."
    exit 1
fi

# Step 2: Check if python3 version is >= 3.6
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
REQUIRED_VERSION="3.6"

if [[ $(echo -e "$PYTHON_VERSION\n$REQUIRED_VERSION" | sort -V | head -n1) != "$REQUIRED_VERSION" ]]; then
    echo "Error: 'soundbase' requires Python version >= 3.6. Installed version is $PYTHON_VERSION. Please upgrade your Python version."
    exit 1
fi

# Define variables
DOT_SOUNDBASE_DIR="$HOME/.soundbase"
VENV_DIR="$DOT_SOUNDBASE_DIR/sbenv"
SOUNDBASE_ENV_BIN_DIR="$VENV_DIR/bin"
REPO_URL="https://github.com/indrajit912/SoundBase.git"

# Step 3: Ensure the base directory exists
if [ ! -d "$DOT_SOUNDBASE_DIR" ]; then
    print_message "Creating base directory $DOT_SOUNDBASE_DIR..."
    mkdir -p "$DOT_SOUNDBASE_DIR"
fi

# Step 4: Install virtualenv if not already installed
if ! command -v virtualenv &> /dev/null; then
    print_message "Installing virtualenv..."
    python3 -m pip install --user virtualenv
fi

# Step 5a: Check if VENV_DIR exists and delete it if it does
if [ -d "$VENV_DIR" ]; then
    print_message "Deleting existing venv directory $VENV_DIR..."
    rm -rf "$VENV_DIR"
fi

# Step 5b: Create a virtual environment
print_message "Creating virtual environment in $VENV_DIR..."
python3 -m virtualenv "$VENV_DIR"


# Step 6: Install the package inside the virtual environment
print_message "Installing vaultsafe from $REPO_URL..."
"$VENV_DIR/bin/python" -m pip install git+"$REPO_URL"

# Step 7: Add the venv/bin directory to the PATH
# Check and update .bashrc
if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.bashrc"; then
        print_message "Adding $SOUNDBASE_ENV_BIN_DIR to PATH in ~/.bashrc..."
        echo "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" >> "$HOME/.bashrc"
    fi
else
    print_message "~/.bashrc file does not exist."
fi

# Check and update .zshrc
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.zshrc"; then
        print_message "Adding $SOUNDBASE_ENV_BIN_DIR to PATH in ~/.zshrc..."
        echo "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" >> "$HOME/.zshrc"
    fi
else
    print_message "~/.zshrc file does not exist."
fi

# Check and update .bash_profile
if [ -f "$HOME/.bash_profile" ]; then
    if ! grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.bash_profile"; then
        print_message "Adding $SOUNDBASE_ENV_BIN_DIR to PATH in ~/.bash_profile..."
        echo "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" >> "$HOME/.bash_profile"
    fi
else
    print_message "~/.bash_profile file does not exist."
fi

print_message "Setup complete! You can now use the 'vaultsafe' command."
print_message "Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."

THIS_SCRIPT="$HOME/Downloads/install_soundbase.sh"
if [ -f "$THIS_SCRIPT" ]; then
    echo "$THIS_SCRIPT exists. Deleting..."
    rm "$THIS_SCRIPT"
    echo "$THIS_SCRIPT has been deleted."
else
    echo "$THIS_SCRIPT does not exist."
fi