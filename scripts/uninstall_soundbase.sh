#!/bin/bash
#
# SoundBase Uninstallation Script
#
# Author: Indrajit Ghosh
# Created On: Jan 03, 2025
#
# Description:
# This script uninstalls the SoundBase application by performing the following:
#   1. Removing the virtual environment and its associated files.
#   2. Removing the SoundBase installation from the system.
#   3. Removing references to the virtual environment from PATH in shell profile files.
#
# Usage:
# Run this script using:
#   ./uninstall.sh
#
# Notes:
# - This script will delete the virtual environment, SoundBase installation, and soundbase.db from your system.
# - If you need to keep the soundbase.db file, please stop now and download a copy using the SoundBase app.
# - Once you have backed up the database, you can safely re-run this uninstallation script.

# Function to print messages
function print_message() {
    echo -e "\033[1;31m$1\033[0m"
}

# Define variables
DOT_SOUNDBASE_DIR="$HOME/.soundbase"
VENV_DIR="$DOT_SOUNDBASE_DIR/sbenv"
SOUNDBASE_ENV_BIN_DIR="$VENV_DIR/bin"
SOUNDBASE_DB_FILE="$DOT_SOUNDBASE_DIR/soundbase.db"

# Step 1: Inform the user about potential data loss
print_message "WARNING: This script will delete the soundbase.db file located in $DOT_SOUNDBASE_DIR."
print_message "If you need to keep the soundbase.db for your own use, please stop now and download a copy using the SoundBase app."
print_message "Once you have backed up the database, you can safely re-run this uninstallation script."

read -p "Do you want to continue with the uninstallation? (y/n): " choice
if [[ "$choice" != "y" ]]; then
    print_message "Uninstallation aborted by the user. Please backup your data before proceeding."
    exit 0
fi

# Step 2: Remove the soundbase.db file
if [ -f "$SOUNDBASE_DB_FILE" ]; then
    print_message "Deleting soundbase.db file..."
    rm "$SOUNDBASE_DB_FILE"
else
    print_message "No soundbase.db file found."
fi

# Step 3: Remove the virtual environment
if [ -d "$VENV_DIR" ]; then
    print_message "Deleting the virtual environment directory $VENV_DIR..."
    rm -rf "$VENV_DIR"
else
    print_message "No virtual environment found at $VENV_DIR."
fi

# Step 4: Remove SoundBase application installation
print_message "Removing SoundBase installation from $DOT_SOUNDBASE_DIR..."
rm -rf "$DOT_SOUNDBASE_DIR"

# Step 5: Remove the virtual environment from PATH in shell profile files

# Check and update .bashrc
if [ -f "$HOME/.bashrc" ]; then
    if grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.bashrc"; then
        print_message "Removing $SOUNDBASE_ENV_BIN_DIR from PATH in ~/.bashrc..."
        # Use sed with escaping for special characters
        sed -i '/export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR/d' "$HOME/.bashrc"
    else
        print_message "$SOUNDBASE_ENV_BIN_DIR not found in ~/.bashrc."
    fi
else
    print_message "~/.bashrc file does not exist."
fi

# Check and update .zshrc
if [ -f "$HOME/.zshrc" ]; then
    if grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.zshrc"; then
        print_message "Removing $SOUNDBASE_ENV_BIN_DIR from PATH in ~/.zshrc..."
        # Use sed with escaping for special characters
        sed -i '/export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR/d' "$HOME/.zshrc"
    else
        print_message "$SOUNDBASE_ENV_BIN_DIR not found in ~/.zshrc."
    fi
else
    print_message "~/.zshrc file does not exist."
fi

# Check and update .bash_profile
if [ -f "$HOME/.bash_profile" ]; then
    if grep -q "export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR" "$HOME/.bash_profile"; then
        print_message "Removing $SOUNDBASE_ENV_BIN_DIR from PATH in ~/.bash_profile..."
        # Use sed with escaping for special characters
        sed -i '/export PATH=\$PATH:$SOUNDBASE_ENV_BIN_DIR/d' "$HOME/.bash_profile"
    else
        print_message "$SOUNDBASE_ENV_BIN_DIR not found in ~/.bash_profile."
    fi
else
    print_message "~/.bash_profile file does not exist."
fi

# Step 6: Final cleanup
print_message "Uninstallation complete!"
print_message "Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to apply changes."
