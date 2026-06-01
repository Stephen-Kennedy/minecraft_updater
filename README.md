# Minecraft Bedrock Server Update Script

This script updates one or more local Minecraft Bedrock Dedicated Server instances on Stephen's Ubuntu Minecraft VM.

## What It Does

- Downloads the requested Bedrock Dedicated Server Linux zip.
- Rejects suspiciously small downloads before touching running services.
- Validates the zip with `unzip -t`.
- Optionally runs system package maintenance.
- Backs up the target server directory with a timestamped tarball.
- Preserves `server.properties`, `worlds`, `allowlist.json`, `permissions.json`, and `mcinput.pipe`.
- Updates the selected server instance.
- Restores preserved files, fixes ownership, and restarts the service.

## Supported Targets

| Target | Path | Service | Port |
| --- | --- | --- | --- |
| `live` | `/usr/games/minecraft_bedrock` | `minecraft-bedrock.service` | `19132` |
| `atlas` | `/usr/games/minecraft_bedrock_atlas` | `minecraft-bedrock-atlas.service` | `19135` |
| `both` | Updates live, then Atlas | Both services | Both |

## Usage

Run with sudo:

```bash
cd /home
sudo python3 mc_update.py
```

The script will prompt for the Bedrock version and target.

You can also run it non-interactively:

```bash
sudo python3 mc_update.py --version 1.26.23.1 --target live
sudo python3 mc_update.py --version 1.26.23.1 --target atlas
sudo python3 mc_update.py --version 1.26.23.1 --target both
```

Skip apt maintenance when you only want to update Minecraft:

```bash
sudo python3 mc_update.py --version 1.26.23.1 --target both --skip-system-update
```

## Backups

Backups are written to:

```text
/usr/games/backups_minecraft_bedrock/
```

Example:

```text
/usr/games/backups_minecraft_bedrock/2026-05-31-214500.live.minecraft_bedrock.tgz
```

## Important Version Note

Use the exact version string from the official Bedrock Dedicated Server Linux download URL.

Example:

```text
1.26.23.1
```

Do not add an extra zero unless the official URL includes it. A wrong version can produce a failed or empty download.

## Requirements

- Python 3
- `sudo`
- `wget`
- `unzip`
- `tar`
- `systemctl`
- A `minecraft` Linux user/group

## Version

Script version: 1.3

Author: Stephen J. Kennedy
