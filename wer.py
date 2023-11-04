#!/usr/bin/env python3

import click
import glob
import os
import platform
import shutil
import subprocess
import tomllib
from typing import Any, List
from itertools import chain


# Configuration utilities
def get_config() -> dict[str, Any]:
    with open("wer.toml", "rb") as f:
        return tomllib.load(f)

def get_platform_config(config) -> dict[str, Any] | None:
    if platform.system() == "Windows":
        return config.get("windows")
    
    return config.get("unix")

def get_generator(config) -> str | None:
    if platform_config := get_platform_config(config):
        return platform_config.get("generator")

    return config["build"].get("generator")


def get_c_compiler(config) -> str | None:
    if platform_config := get_platform_config(config):
        return platform_config.get("cc")

def get_cxx_compiler(config) -> str | None:
    if platform_config := get_platform_config(config):
        return platform_config.get("cxx")

def get_format_style(config) -> str | None:
    if format_config := config.get("format"):
        return format_config.get("style")

def get_format_files(config) -> List[str]:
    recursive_glob = lambda x: glob.glob(x, recursive=True)

    if not (format_config := config.get("format")):
        return []

    format_glob = format_config.get("glob")
    format_files = map(recursive_glob, format_glob)

    # Flatten and dedup
    return list(set(chain.from_iterable(format_files)))

def get_vcpkg_bootstrap() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\bootstrap-vcpkg.bat"
    
    return "./vcpkg/bootstrap-vcpkg.sh"

def get_vcpkg_exe() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\vcpkg.exe"

    return "./vcpkg/vcpkg"

def create_env_vars(config, create_ccs: bool) -> dict[str, str]:
    env_vars = {
        **os.environ,
        "CMAKE_EXPORT_COMPILE_COMMANDS": str(int(create_ccs))
    }

    if c_compiler := get_c_compiler(config):
        env_vars["CC"] = c_compiler

    if cpp_compiler := get_cxx_compiler(config):
        env_vars["CXX"] = cpp_compiler

    return env_vars

def create_cmake_commands(
        build_dir: str,
        generator: str | None,
        enable_vcpkg: bool,
        vcpkg_dir: str
) -> List[str]:
    commands = ["cmake", "-S", ".", "-B", build_dir]

    if generator:
        commands.append(f"-G {generator}")

    if enable_vcpkg:
        if os.path.exists(vcpkg_dir):
            commands.append(f"-DCMAKE_TOOLCHAIN_FILE={vcpkg_dir}/scripts/buildsystems/vcpkg.cmake")
        else:
            click.echo("Please first run `./wer.py vcpkg setup` or disable vcpkg on `wer.toml`")
            raise FileNotFoundError

    return commands


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
def format():
    """Formats source files. Defaults to LLVM style."""
    if format_files := get_format_files(CONFIG):
        commands = ["clang-format", *format_files]

        if format_style := get_format_style(CONFIG):
            commands.append(f"-style={format_style}")

        subprocess.run(commands)
    else:
        click.echo("Please provide directories in `wer.toml`")
        return


@cli.command()
@click.option("--create-ccs", default=True, help="Create compile_commands.json")
def configure(create_ccs):
    """Configures the project"""

    click.echo("Configuring the project...")

    # There should be a better way to do this
    env_vars = create_env_vars(CONFIG, create_ccs)
    commands = create_cmake_commands(BUILD_DIR,
                                     GENERATOR,
                                     VCPKG_ENABLE,
                                     VCPKG_DIR)

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
