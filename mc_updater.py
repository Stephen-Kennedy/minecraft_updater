#!/usr/bin/python3
# Author Stephen J Kennedy
# Version 1.3
# Script to update Minecraft Bedrock server instances.

import argparse
import datetime
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DOWNLOAD_BASE_URL = "https://www.minecraft.net/bedrockdedicatedserver/bin-linux"
DOWNLOAD_DIRECTORY = Path("/usr/games")
BACKUP_DIRECTORY = Path("/usr/games/backups_minecraft_bedrock")
USER_AGENT = "Mozilla/5.0"
PRESERVE_ITEMS = (
    "server.properties",
    "worlds",
    "allowlist.json",
    "permissions.json",
    "mcinput.pipe",
)

INSTANCES = {
    "live": {
        "name": "live",
        "path": Path("/usr/games/minecraft_bedrock"),
        "service": "minecraft-bedrock.service",
    },
    "atlas": {
        "name": "atlas",
        "path": Path("/usr/games/minecraft_bedrock_atlas"),
        "service": "minecraft-bedrock-atlas.service",
    },
}


def sudo_prefix():
    return [] if os.geteuid() == 0 else ["sudo"]


def run_command(command, error_message, cwd=None):
    try:
        logging.info("Running: %s", " ".join(str(part) for part in command))
        return subprocess.run(command, text=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as error:
        logging.error("%s", error_message)
        sys.exit(error.returncode)


def system_update():
    for action in ("update", "upgrade", "autoremove", "autoclean"):
        run_command(sudo_prefix() + ["apt", "-y", action], f"Failed to apt {action}")


def manage_service(action, service_name):
    run_command(sudo_prefix() + ["systemctl", action, service_name], f"Failed to {action} {service_name}")


def download_server(version):
    DOWNLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    zip_path = DOWNLOAD_DIRECTORY / f"bedrock-server-{version}.zip"
    url = f"{DOWNLOAD_BASE_URL}/bedrock-server-{version}.zip"

    if zip_path.exists():
        zip_path.unlink()

    run_command(
        [
            "wget",
            f"--user-agent={USER_AGENT}",
            "-O",
            str(zip_path),
            url,
        ],
        f"Failed to download Minecraft server from {url}",
    )

    if zip_path.stat().st_size < 1_000_000:
        logging.error("Downloaded file is suspiciously small: %s (%s bytes)", zip_path, zip_path.stat().st_size)
        sys.exit(1)

    run_command(["unzip", "-t", str(zip_path)], "Downloaded zip failed validation")
    return zip_path


def make_backup(instance):
    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_path = BACKUP_DIRECTORY / f"{stamp}.{instance['name']}.minecraft_bedrock.tgz"
    source_path = instance["path"]

    if not source_path.exists():
        logging.error("Instance directory does not exist: %s", source_path)
        sys.exit(1)

    run_command(
        sudo_prefix()
        + [
            "tar",
            "-C",
            str(source_path.parent),
            "-czf",
            str(backup_path),
            source_path.name,
        ],
        f"Failed to back up {source_path}",
    )
    logging.info("Backup created: %s", backup_path)
    return backup_path


def preserve_instance_files(instance):
    source_path = instance["path"]
    keep_dir = Path("/tmp") / f"minecraft-update-keep-{instance['name']}-{os.getpid()}"
    if keep_dir.exists():
        shutil.rmtree(keep_dir)
    keep_dir.mkdir(parents=True)

    for item in PRESERVE_ITEMS:
        source = source_path / item
        destination = keep_dir / item
        if source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
        elif source.is_file():
            shutil.copy2(source, destination)

    return keep_dir


def restore_instance_files(instance, keep_dir):
    target_path = instance["path"]
    for item in PRESERVE_ITEMS:
        source = keep_dir / item
        destination = target_path / item
        if not source.exists():
            continue
        if destination.exists() or destination.is_fifo():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        if source.is_dir():
            shutil.copytree(source, destination, symlinks=True)
        else:
            shutil.copy2(source, destination)

    pipe_path = target_path / "mcinput.pipe"
    if pipe_path.exists() and not pipe_path.is_fifo():
        pipe_path.unlink()
    if not pipe_path.exists():
        run_command(sudo_prefix() + ["mkfifo", str(pipe_path)], f"Failed to create {pipe_path}")
    run_command(sudo_prefix() + ["chmod", "660", str(pipe_path)], f"Failed to set permissions for {pipe_path}")

    shutil.rmtree(keep_dir)


def update_instance(instance, zip_path):
    target_path = instance["path"]
    service_name = instance["service"]

    make_backup(instance)
    keep_dir = preserve_instance_files(instance)
    manage_service("stop", service_name)

    run_command(
        sudo_prefix() + ["unzip", "-o", str(zip_path), "-d", str(target_path)],
        f"Failed to unzip Minecraft server into {target_path}",
    )
    restore_instance_files(instance, keep_dir)

    run_command(
        sudo_prefix() + ["chown", "-R", "minecraft:minecraft", str(target_path)],
        f"Failed to change ownership for {target_path}",
    )
    manage_service("start", service_name)
    manage_service("status", service_name)


def selected_instances(target):
    if target == "both":
        return [INSTANCES["live"], INSTANCES["atlas"]]
    return [INSTANCES[target]]


def parse_args():
    parser = argparse.ArgumentParser(description="Update Minecraft Bedrock server instances.")
    parser.add_argument("--version", help="Bedrock Dedicated Server version, for example 1.26.23.1")
    parser.add_argument(
        "--target",
        choices=("live", "atlas", "both"),
        default="live",
        help="Server instance to update. Default: live",
    )
    parser.add_argument(
        "--skip-system-update",
        action="store_true",
        help="Skip apt update/upgrade/autoremove/autoclean.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if os.geteuid() != 0:
        logging.error("Run this script with sudo so it can preserve files and manage services safely.")
        sys.exit(1)

    version = args.version or input("Please enter the Minecraft server version (e.g., 1.26.23.1): ").strip()
    if not version:
        logging.error("Version is required.")
        sys.exit(1)

    target = args.target
    if not args.version:
        target_input = input("Update which server? live, atlas, or both [live]: ").strip().lower()
        if target_input:
            target = target_input
    if target not in ("live", "atlas", "both"):
        logging.error("Invalid target: %s", target)
        sys.exit(1)

    zip_path = download_server(version)
    if not args.skip_system_update:
        system_update()

    for instance in selected_instances(target):
        update_instance(instance, zip_path)

    logging.info("Minecraft Bedrock update complete for target=%s version=%s", target, version)


if __name__ == "__main__":
    main()
