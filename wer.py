#!/usr/bin/env python3

import click
import os
import platform
import shutil
import subprocess
import tomllib


# Utility
def get_config():
    with open("wer.toml", "rb") as f:
        return tomllib.load(f)

def get_vcpkg_bootstrap() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\bootstrap-vcpkg.bat"
    
    return "./vcpkg/bootstrap-vcpkg.sh"

def get_vcpkg_exe() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\vcpkg.exe"

    return "./vcpkg/vcpkg"

def get_generator(config) -> str:
    platform_config = None

    if platform.system() == "Windows":
        platform_config = config.get("windows")
    else:
        platform_config = config.get("unix")

    if platform_config:
        return platform_config.get("generator")

    return config["build"].get("generator")


# Main group
@click.group()
def cli():
    """Building runner"""
    pass


@cli.command()
def build():
    """Builds everything"""

    if os.path.exists(BUILD_DIR):
        click.echo("Building...")
        subprocess.run(["cmake", "--build", BUILD_DIR])
    else:
        click.echo("Please first run `./wer.py configure`")


@cli.command()
def clean():
    """Cleans everything"""

    click.echo("Cleaning everything...")

    try:
        shutil.rmtree(BUILD_DIR)
    except FileNotFoundError:
        click.echo("Already cleaned up!")


@cli.command()
@click.option("--create-ccs", default=True, help="Create compile_commands.json")
def configure(create_ccs):
    """Configures the project"""

    click.echo("Configuring the project...")

    # There should be a better way to do this
    env_vars = {
        **os.environ,
        "CMAKE_EXPORT_COMPILE_COMMANDS": str(int(create_ccs))
    }

    commands = ["cmake", "-S", ".", "-B", BUILD_DIR]

    if GENERATOR:
        commands.append(f"-G {GENERATOR}")

    if VCPKG_ENABLE:
        if os.path.exists(VCPKG_DIR):
            commands.append(f"-DCMAKE_TOOLCHAIN_FILE={VCPKG_DIR}/scripts/buildsystems/vcpkg.cmake")
        else:
            click.echo("Please first run `./wer.py vcpkg setup` or disable vcpkg on `wer.toml`")
            return

    subprocess.run(commands, env=env_vars)


# vcpkg related
@cli.group()
def vcpkg():
    """vcpkg management"""
    pass


@vcpkg.command()
def install():
    """Installs all vcpkg libraries"""

    if not os.path.exists(VCPKG_DIR):
        click.echo("Please first run `./wer.py vcpkg setup`")
        return

    click.echo("Installing packages...")
    subprocess.run([VCPKG_EXE, "install"])


@vcpkg.command()
def setup():
    """Installs vcpkg"""

    if os.path.exists(VCPKG_DIR):
        click.echo("vcpkg already fetched!")
    else:
        subprocess.run(["git", "clone", VCPKG_REPO])

    click.echo("Installing vcpkg...")
    subprocess.run([VCPKG_SCRIPT, "-disableMetrics"])


@vcpkg.command()
def uninstall():
    """Removes all vcpkg related things"""

    try:
        shutil.rmtree(VCPKG_DIR)
    except FileNotFoundError:
        click.echo("vcpkg already removed!")

    try:
        shutil.rmtree(VCPKG_INSTALL_DIR)
    except FileNotFoundError:
        click.echo("vcpkg_installed already removed!")


# Global variables
CONFIG = get_config()
BUILD_DIR = CONFIG["build"]["dir"]
GENERATOR = get_generator(CONFIG)

VCPKG_ENABLE = CONFIG["vcpkg"]["enable"]

VCPKG_REPO = "https://github.com/Microsoft/vcpkg.git"
VCPKG_DIR = "vcpkg"
VCPKG_INSTALL_DIR = "vcpkg_installed"
VCPKG_SCRIPT = get_vcpkg_bootstrap()
VCPKG_EXE = get_vcpkg_exe()

if __name__ == "__main__":
    cli()
