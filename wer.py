#!/usr/bin/env python3

import click
import glob
import os
import platform
import shutil
import subprocess
import tomllib
from typing import Any, List, Set
from itertools import chain


class WerConfig:
    cached_config: dict[str, Any] = {}

    def __init__(self):
        if not self.cached_config:
            self.cached_config = WerConfig.load_config()
        
        self.config = self.cached_config
        self.build_dir: str = self.config["build"]["dir"]
        self.build_config: dict[str, Any] = self.config["build"]
        self.format_config: dict[str, Any] = self.config.get("format")
        self.platform_config = WerConfig.get_platform_config(self.config)

        self.enable_vcpkg: str | None = self.config.get("enable")
    
    def load_config() -> dict[str, Any]:
        with open("wer.toml", "rb") as f:
            return tomllib.load(f)
    
    def get_platform_config(config: dict[str, Any]) -> dict[str, Any] | None:
        match platform.system():
            case "Windows" :
                return config.get("windows")
            
            case "Linux" :
                if linux_config := config.get("linux"):
                    return linux_config
            
            case "Darwin" :
                if darwin_config := config.get("darwin"):
                    return darwin_config
        
        return config.get("unix")
    
    @property
    def generator(self) -> str | None:
        if self.platform_config:
            return self.platform_config.get("generator")
        
        return self.config.get("generator")
    
    @property
    def c_compiler(self) -> str | None:
        if self.platform_config:
            return self.platform_config.get("cc")
    
    @property
    def cxx_compiler(self) -> str | None:
        if self.platform_config:
            return self.platform_config.get("cxx")
    
    @property
    def fmt_style(self) -> str | None:
        if self.format_config:
            return self.format_config.get("style")

    @property
    def fmt_files(self) -> Set[str]:
        recursive_glob = lambda x: glob.glob(x, recursive=True)

        if not self.format_config:
            return set()
        
        format_glob = self.format_config.get("glob")
        format_files = map(recursive_glob, format_glob)

        # Dedup and remove excluded files
        return set(chain.from_iterable(format_files)) - self.excluded_fmt_files

    @property
    def excluded_fmt_files(self) -> Set[str]:
        if self.format_config:
            if excluded_files := self.format_config.get("exclude"):
                return set(excluded_files)

        return set()
    

def get_vcpkg_bootstrap() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\bootstrap-vcpkg.bat"
    
    return "./vcpkg/bootstrap-vcpkg.sh"

def get_vcpkg_exe() -> str:
    if platform.system() == "Windows":
        return ".\vcpkg\vcpkg.exe"

    return "./vcpkg/vcpkg"

def create_env_vars(config: WerConfig, create_ccs: bool) -> dict[str, str]:
    env_vars = {
        **os.environ,
        "CMAKE_EXPORT_COMPILE_COMMANDS": str(int(create_ccs))
    }

    if config.c_compiler:
        env_vars["CC"] = config.c_compiler
    
    if config.cxx_compiler:
        env_vars["CXX"] = config.cxx_compiler
    
    return env_vars

def create_cmake_commands(config: WerConfig, vcpkg_dir: str) -> List[str]:
    commands = ["cmake", "-S", ".", "-B", config.build_dir]

    if config.generator:
        commands.append(f"-G {config.generator}")

    if config.enable_vcpkg:
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

    if os.path.exists(WER_CONFIG.build_dir):
        click.echo("Building...")
        subprocess.run(["cmake", "--build", WER_CONFIG.build_dir])
    else:
        click.echo("Please first run `./wer.py configure`")


@cli.command()
def clean():
    """Cleans everything"""

    click.echo("Cleaning everything...")

    try:
        shutil.rmtree(WER_CONFIG.build_dir)
    except FileNotFoundError:
        click.echo("Already cleaned up!")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Run without doing any changes")
@click.option("--list", is_flag=True, help="Lists which files are going to be formatted")
def format(dry_run, list):
    """Formats source files. Defaults to LLVM style."""
    if not shutil.which("clang-format"):
        click.echo("Can't find `clang-format`")
        return

    if format_files := sorted(WER_CONFIG.fmt_files):
        if list:
            click.echo('\n'.join(format_files))
            return

        commands = ["clang-format", *format_files]

        if not dry_run:
            commands.append("-i")

        if format_style := WER_CONFIG.fmt_style:
            commands.append(f"-style={format_style}")

        subprocess.run(commands)
    else:
        click.echo("Please provide directories in `wer.toml`")
        return


@cli.command()
@click.option("--create-ccs", is_flag=True, default=True, help="Create compile_commands.json")
def configure(create_ccs):
    """Configures the project"""

    click.echo("Configuring the project...")

    # There should be a better way to do this
    env_vars = create_env_vars(WER_CONFIG, create_ccs)
    commands = create_cmake_commands(WER_CONFIG, VCPKG_DIR)

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


WER_CONFIG = WerConfig()

VCPKG_REPO = "https://github.com/Microsoft/vcpkg.git"
VCPKG_DIR = "vcpkg"
VCPKG_INSTALL_DIR = "vcpkg_installed"
VCPKG_SCRIPT = get_vcpkg_bootstrap()
VCPKG_EXE = get_vcpkg_exe()


if __name__ == "__main__":
    cli()
