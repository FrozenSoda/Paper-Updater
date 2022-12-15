#!/usr/bin/python3
from __future__ import annotations

import argparse
import re
import os
import json
import requests


class LocalServerBuild:
    def __init__(self, mc_version: str, build_num: int):
        self.mc_version = mc_version
        self.build_num = build_num

    @staticmethod
    def get_latest(mc_version: str, server_dir: str) -> LocalServerBuild:
        filename_pattern = r"^paper-{}-(.*).jar$".format(mc_version)

        # Find the newest existing build jar in script dir
        latest_installed_build_num = -1
        for filename in os.listdir(server_dir):
            if not re.match(filename_pattern, filename):
                # file is not a Paper jar file
                continue

            try:
                build_num = int(re.search(filename_pattern, filename).group(1))
            except ValueError:
                continue

            if build_num > latest_installed_build_num:
                latest_installed_build_num = build_num

        return LocalServerBuild(mc_version, latest_installed_build_num)


class OnlineServerBuild:
    builds_url_template = "https://papermc.io/api/v2/projects/paper/versions/{}/builds"
    download_url_template = \
        "https://papermc.io/api/v2/projects/paper/versions/{0}/builds/{1}/downloads/paper-{0}-{1}.jar"

    def __init__(self, mc_version: str, build_num: int, download_size: int, download_url: str):
        self.mc_version = mc_version
        self.build_num = build_num
        self.download_size = download_size
        self.download_url = download_url

    @staticmethod
    def get_latest(mc_version: str) -> OnlineServerBuild:
        print('Checking for updates ...')

        response = requests.get(OnlineServerBuild.builds_url_template.format(mc_version))
        response.raise_for_status()
        response_json = json.loads(response.text)
        non_experimental_builds = [build for build in response_json['builds'] if build['channel'] == 'default']

        if len(non_experimental_builds) == 0:
            raise ValueError('No non-experimental builds are available for the specified Minecraft version.')

        latest_non_experimental_build = non_experimental_builds[-1]
        latest_build_num = latest_non_experimental_build['build']

        download_url = OnlineServerBuild.download_url_template.format(mc_version, latest_build_num)
        download_headers = requests.head(download_url)
        download_size = int(download_headers.headers['Content-Length'])

        return OnlineServerBuild(mc_version, latest_build_num, download_size, download_url)

    def update_to(self, *, server_dir: str, start_script_name: str) -> None:
        # UPDATE SERVER JAR

        installed_build = LocalServerBuild.get_latest(self.mc_version, server_dir)

        if self.build_num <= installed_build.build_num:
            print('No updates are available (current build: {})'.format(installed_build.build_num))
            return
        print('An update is available!')
        print('New Build:         {}'.format(self.build_num))
        if installed_build.build_num > -1:
            print('Installed Build:   {}'.format(installed_build.build_num))
        else:
            print('Installed Build:   No installed build was found')
        print('Download Size:     {}'.format(sizeof_fmt(self.download_size)))

        print('Downloading update...')
        filepath = os.path.join(server_dir, "paper-{}-{}.jar".format(self.mc_version, self.build_num))
        jar = requests.get(self.download_url, allow_redirects=True)
        with open(filepath, 'wb') as file:
            file.write(jar.content)

        # UPDATE SERVER SCRIPT

        jar_pattern_general = r"paper-(.*).jar"
        print('Updating server script...')
        start_script_path = os.path.join(server_dir, start_script_name)
        if os.path.isfile(start_script_path):
            with open(start_script_path, 'r') as file:
                start_script = file.read()

            # replace Paper jar filename in script with the filename of the new jar
            start_script = re.sub(jar_pattern_general, os.path.basename(filepath), start_script)

            with open(start_script_path, 'w') as file:
                file.write(start_script)
        else:
            print("ERROR: Start script path '{}' cannot be found. Please update your server script manually.".format(
                start_script_path))

        print("Update finished!")


def cls() -> None:
    """Clears the terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def sizeof_fmt(num: int, suffix: str = 'B') -> str:
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def print_title(s: str) -> None:
    """Prints a nice looking title for menus, where 's' is a string consisting of the title text"""

    cls()
    print(s.upper())
    print("=" * len(s))
    print("")


def main() -> None:
    parser = argparse.ArgumentParser(description='Update your Minecraft Paper server effortlessly.')

    parser.add_argument('--server-dir',
                        help='The full path to the directory where the server files reside.',
                        required=True)
    parser.add_argument('--minecraft-version',
                        help='The desired Minecraft version of the build to be downloaded.',
                        required=True)
    parser.add_argument('--start-script-name',
                        help='The name of the server start script that resides in the server dir, '
                             'including its file extension.',
                        default='start_noupdate.sh')

    args = parser.parse_args()

    if args.server_dir is not None:
        args.server_dir = os.path.expanduser(args.server_dir)

    latest_build = OnlineServerBuild.get_latest(args.minecraft_version)
    latest_build.update_to(server_dir=args.server_dir, start_script_name=args.start_script_name)


if __name__ == '__main__':
    main()
