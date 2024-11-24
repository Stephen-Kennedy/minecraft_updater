README

Minecraft Bedrock Server Update Script

Overview

This script, authored by Stephen J. Kennedy, automates the process of updating a Minecraft Bedrock server along with performing system updates. The script includes functionality to:
	•	Stop the Minecraft server service.
	•	Perform system package updates and cleanup.
	•	Backup the existing server directory.
	•	Download and install the specified version of the Minecraft Bedrock server.
	•	Restore critical files from the backup (e.g., server.properties, worlds).
	•	Update file ownership and restart the Minecraft service.

Features

	•	Automated System Maintenance: Runs apt commands to keep the system updated.
	•	Backup & Restore: Safeguards current server configurations and worlds during updates.
	•	Minecraft Server Management: Integrates with systemctl to manage the Minecraft Bedrock service.
	•	Custom Version Support: Prompts for the desired Minecraft server version to install.

Requirements

	•	Python 3.x
	•	A Linux-based system with:
	•	wget, unzip, apt, and systemctl commands available.
	•	Sufficient permissions to execute system commands (sudo/root access).
	•	Minecraft Bedrock server files should reside in /usr/games/minecraft_bedrock.

Usage

	1.	Clone or Download the Script
Clone this repository or download the script directly.
	2.	Run the Script
Execute the script using Python 3:

python3 update_minecraft_bedrock.py


	3.	Follow the Prompts
Enter the desired Minecraft Bedrock version when prompted (e.g., 1.17.10.04).
	4.	Process Flow
	•	The script stops the Minecraft service.
	•	Updates the system packages.
	•	Backs up the existing Minecraft server files.
	•	Downloads the specified version of the Minecraft Bedrock server.
	•	Restores important configuration files and worlds.
	•	Starts the Minecraft service.

Directory Structure

	•	Minecraft Bedrock Server Path: /usr/games/minecraft_bedrock
	•	Backup Path: /usr/games/backups_minecraft_bedrock/YYYY-MM-DD.minecraft_bedrock.bak

Configuration

The script uses hardcoded paths and service names:
	•	Minecraft Instance Directory: /usr/games/minecraft_bedrock
	•	Service Name: minecraft-bedrock.service

You may modify these paths and names in the script if your setup differs.

Logging

The script uses Python’s logging module to record:
	•	Successful commands.
	•	Errors and warnings.
	•	Backup creation and restoration processes.

Logs are output directly to the console.

Example Output

2024-11-24 14:32:00 - INFO - Command executed successfully: apt -y update
2024-11-24 14:32:05 - INFO - Backup created: /usr/games/backups_minecraft_bedrock/2024-11-24.minecraft_bedrock.bak
2024-11-24 14:32:10 - INFO - Downloaded and unzipped Minecraft server version 1.17.10.04
2024-11-24 14:32:15 - INFO - Started the Minecraft service

Troubleshooting

	1.	Permission Errors: Ensure the script is executed with sufficient privileges (sudo).
	2.	Download Issues: Confirm the Minecraft Bedrock server URL is valid and accessible.
	3.	Restore Warnings: If the server.properties or worlds directory is missing in the backup, you may need to manually configure them.

Version

	•	Script Version: 1.2

Author

Stephen J. Kennedy
For questions or issues, please contact GitHub Issues.

This script is provided as-is, with no warranty or guarantee. Use at your own risk.
