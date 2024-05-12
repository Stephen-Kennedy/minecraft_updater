#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.1
# Script to update Minecraft Bedrock version along with system updates

import datetime
import logging
import os
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_command(command, error_message, cwd=None):
    """Executes a shell command in a given directory and handles errors."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True, cwd=cwd)
        logging.info(f"Command executed successfully: {' '.join(command) if isinstance(command, list) else command}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"{error_message}: {e.stderr}")
        sys.exit(1)


def system_update():
    """Updates the system packages and cleans up."""
    updates = ['update', 'upgrade', 'autoremove', 'autoclean']
    for update in updates:
        run_command(f'apt -y {update}', f'Failed to {update} system packages')


def download_and_unzip_minecraft_server(version, download_directory, unzip_directory):
    """Downloads and unzips the Minecraft server."""
    url = f"https://minecraft.azureedge.net/bin-linux/bedrock-server-{version}.zip"
    file_path = os.path.join(download_directory, f"bedrock-server-{version}.zip")

    # Download server
    wget_command = f"wget -P {download_directory} {url}"
    run_command(wget_command, "Failed to download Minecraft server")

    # Unzip server
    unzip_command = f"unzip -o {file_path} -d {unzip_directory}"
    run_command(unzip_command, "Failed to unzip Minecraft server", cwd=download_directory)
    os.remove(file_path)  # Clean up zip file after extraction


def manage_minecraft_server(action, service_name):
    """Starts, stops, or restarts the Minecraft server."""
    systemctl_command = f"sudo systemctl {action} {service_name}"
    run_command(systemctl_command, f"Failed to {action} the Minecraft service")


def main():
    mc_instance = "/usr/games/minecraft_bedrock"
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    mc_backup = f"/usr/games/backups_minecraft_bedrock/{current_date}.minecraft_bedrock.bak"
    minecraft_service = "minecraft-bedrock.service"
    download_directory = "/usr/games"
    unzip_directory = mc_instance

    version = input("Please enter the Minecraft server version (e.g., 1.17.10.04): ")

    # Ensure Minecraft service is stopped before proceeding
    manage_minecraft_server('stop', minecraft_service)

    # Perform system updates
    system_update()

    # Backup existing server directory
    if os.path.exists(mc_instance):
        if os.path.exists(mc_backup):
            run_command(f"rm -rf {mc_backup}", "Failed to remove old backup directory")
        os.rename(mc_instance, mc_backup)
        logging.info(f"Backup created: {mc_backup}")
    else:
        logging.error(f"Directory does not exist: {mc_instance}")
        sys.exit(1)

    # Download and setup the new server
    download_and_unzip_minecraft_server(version, download_directory, unzip_directory)

    # Restore configurations from backup
    if os.path.exists(os.path.join(mc_backup, "server.properties")):
        os.rename(os.path.join(mc_backup, "server.properties"), os.path.join(mc_instance, "server.properties"))
    if os.path.exists(os.path.join(mc_backup, "worlds")):
        os.rename(os.path.join(mc_backup, "worlds"), os.path.join(mc_instance, "worlds"))

    # Update file ownership
    chown_command = f"sudo chown -R minecraft:minecraft {mc_instance}"
    run_command(chown_command, "Failed to change file ownership")

    # Start Minecraft service
    manage_minecraft_server('start', minecraft_service)


if __name__ == "__main__":
    main()
